import urllib.request
import urllib.parse
import ssl
import json

def query(sql):
    url = 'https://vault-in.hdel.co.kr:8070/api/executeQuery'
    params = {'key': 'subae', 'sql': sql}
    full_url = url + '?' + urllib.parse.urlencode(params)
    ctx = ssl._create_unverified_context()
    req = urllib.request.Request(full_url, headers={'Accept': 'application/json', 'User-Agent': 'Mozilla/5.0'})
    with urllib.request.urlopen(req, context=ctx, timeout=120) as resp:
        return json.loads(resp.read().decode('utf-8', errors='replace'))

print("--- ELV_INFO$VF MD$NUMBER 샘플 20개 ---")
sql = "SELECT MD$NUMBER, EL_ABRAND, COD(EL_ABRAND) AS BRAND, EL_ATYP, COD(EL_ATYP) AS GISONG FROM HDEL_DEFAULT.ELV_INFO$VF WHERE MD$NUMBER IS NOT NULL AND ROWNUM <= 20"
res = query(sql)
print(res)

