param(
    [string]$sqlFile,
    [string]$output,
    [string]$managerFilter
)

$ErrorActionPreference = 'Stop'

# SSL Verification Bypass
[System.Net.ServicePointManager]::SecurityProtocol = [System.Net.SecurityProtocolType]::Tls12 -bor [System.Net.SecurityProtocolType]::Tls11
[System.Net.ServicePointManager]::ServerCertificateValidationCallback = {$true}

# Load SQL
if (-not (Test-Path $sqlFile)) {
    Write-Error "SQL file not found: $sqlFile"
    exit 1
}
$sql = (Get-Content -Raw -Path $sqlFile).Trim()

# URL Encoding
Add-Type -AssemblyName System.Web
try {
    $eucKr = [System.Text.Encoding]::GetEncoding("euc-kr")
    $encodedSql = [System.Web.HttpUtility]::UrlEncode($sql, $eucKr)
} catch {
    $encodedSql = [System.Web.HttpUtility]::UrlEncode($sql)
}

$url = "https://vault-in.hdel.co.kr:8070/api/executeQuery?key=subae&sql=$encodedSql"

Write-Output "Sending request to API..."
$tempResponseFile = [System.IO.Path]::GetTempFileName()
curl.exe -k -s -H "Accept: application/json" -o $tempResponseFile $url
if ($LASTEXITCODE -ne 0) {
    Remove-Item $tempResponseFile -ErrorAction SilentlyContinue
    Write-Error "curl.exe failed with exit code $LASTEXITCODE"
    exit 1
}

$responseRaw = [System.IO.File]::ReadAllText($tempResponseFile, [System.Text.Encoding]::UTF8)
Remove-Item $tempResponseFile -ErrorAction SilentlyContinue

$responseJson = $responseRaw | ConvertFrom-Json

if ($null -eq $responseJson) {
    Write-Error "Empty response from API"
    exit 1
}

# Resolve target path and ensure parent directories exist
$targetPath = $ExecutionContext.SessionState.Path.GetUnresolvedProviderPathFromPSPath($output)
$parentDir = Split-Path -Parent $targetPath
if (-not (Test-Path $parentDir)) {
    New-Item -ItemType Directory -Path $parentDir -Force | Out-Null
}

# Find payload rows
$rows = $null
if ($responseJson -is [System.Array]) {
    $rows = $responseJson
} elseif ($responseJson -is [System.Collections.IDictionary] -or $responseJson -is [PSCustomObject]) {
    $dataKeys = @("data", "rows", "resultList", "list", "items", "results")
    foreach ($key in $dataKeys) {
        if ($responseJson.$key) {
            $rows = $responseJson.$key
            break
        }
    }
    if ($null -eq $rows) {
        foreach ($prop in $responseJson.PSObject.Properties) {
            if ($prop.Value -is [System.Array]) {
                $rows = $prop.Value
                break
            }
        }
    }
}

if ($null -eq $rows) {
    if ($responseJson -is [System.Collections.IDictionary] -or $responseJson -is [PSCustomObject]) {
        $rows = @($responseJson)
    } else {
        Write-Error "Could not find data rows in API response"
        exit 1
    }
}

# Client-side filtering by MANAGER if managerFilter is provided
if ($managerFilter) {
    Write-Output "Filtering rows by MANAGER = $managerFilter..."
    $filteredRowsArray = @()
    foreach ($row in $rows) {
        $mgr = $null
        if ($row -is [System.Management.Automation.PSCustomObject]) {
            $mgr = $row.MANAGER
        } elseif ($row -is [System.Collections.IDictionary]) {
            $mgr = $row["MANAGER"]
        }
        if ($null -ne $mgr -and $mgr.ToString() -like "*$managerFilter*") {
            $filteredRowsArray += $row
        }
    }
    $rows = $filteredRowsArray
}

if ($rows.Count -eq 0) {
    Write-Output "No rows returned from the query."
    Set-Content -Path $targetPath -Value "" -Encoding utf8
    exit 0
}

# Filter out completely empty columns to improve readability
$filteredRows = $rows
if ($rows.Count -gt 0) {
    $allKeys = @()
    if ($rows[0] -is [System.Management.Automation.PSCustomObject]) {
        $allKeys = $rows[0].PSObject.Properties | Select-Object -ExpandProperty Name
    } elseif ($rows[0] -is [System.Collections.IDictionary]) {
        $allKeys = $rows[0].Keys
    }

    $alwaysKeep = @("NO", "ADDR", "GOTO", "REMARKS")
    $validKeys = @()
    foreach ($key in $allKeys) {
        if ($alwaysKeep -contains $key) {
            $validKeys += $key
            continue
        }
        
        $hasValue = $false
        foreach ($row in $rows) {
            $val = $null
            if ($row -is [System.Management.Automation.PSCustomObject]) {
                $val = $row.$key
            } else {
                $val = $row[$key]
            }
            if ($null -ne $val -and $val.ToString().Trim() -ne "") {
                $hasValue = $true
                break
            }
        }
        if ($hasValue) {
            $validKeys += $key
        }
    }

    # Reorder keys according to original index to preserve columns sequence
    $orderedValidKeys = @()
    foreach ($key in $allKeys) {
        if ($validKeys -contains $key) {
            $orderedValidKeys += $key
        }
    }

    $filteredRows = @()
    foreach ($row in $rows) {
        $obj = [Ordered]@{}
        foreach ($key in $orderedValidKeys) {
            $val = $null
            if ($row -is [System.Management.Automation.PSCustomObject]) {
                $val = $row.$key
            } else {
                $val = $row[$key]
            }
            $obj[$key] = $val
        }
        $filteredRows += [PSCustomObject]$obj
    }
}

# Export to CSV with UTF-8 BOM
$tempCsv = [System.IO.Path]::GetTempFileName()
$filteredRows | Export-Csv -Path $tempCsv -NoTypeInformation -Encoding UTF8

$utf8WithBOM = New-Object System.Text.UTF8Encoding($true)
$csvContent = [System.IO.File]::ReadAllText($tempCsv)
[System.IO.File]::WriteAllText($targetPath, $csvContent, $utf8WithBOM)
Remove-Item $tempCsv

Write-Output "CSV Saved: $targetPath / $($rows.Count) rows (Filtered empty columns)"
