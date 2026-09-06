# -*- coding: utf-8 -*-
import json
import urllib.parse
import urllib.request
import ssl

ctx = ssl._create_unverified_context()

def run_sql(sql):
    url = "https://vault-in.hdel.co.kr:8070/api/executeQuery?" + urllib.parse.urlencode({
        "key": "subae",
        "sql": sql
    })
    req = urllib.request.Request(url, headers={"Accept": "application/json"})
    try:
        with urllib.request.urlopen(req, context=ctx, timeout=60) as resp:
            return json.loads(resp.read().decode('utf-8', errors='ignore'))
    except Exception as e:
        return f"Error: {e}"

print("=== 1. HDEL_DEFAULT.PRODUCT$VF 건수 ===")
print(run_sql("SELECT COUNT(*) AS CNT FROM HDEL_DEFAULT.PRODUCT$VF"))

print("\n=== 2. HDEL_DEFAULT.PRODUCT$VF 최근 5건 MD$MDATE ===")
print(run_sql("SELECT MD$NUMBER, MD$MDATE, MD$CDATE FROM (SELECT MD$NUMBER, MD$MDATE, MD$CDATE FROM HDEL_DEFAULT.PRODUCT$VF ORDER BY MD$MDATE DESC) WHERE ROWNUM <= 5"))

print("\n=== 3. HDEL_DEFAULT.BLOCKNO$SF 5건 ===")
print(run_sql("SELECT MD$NUMBER FROM HDEL_DEFAULT.BLOCKNO$SF WHERE ROWNUM <= 5"))

print("\n=== 4. BLOCKNO$SF에서 A101A 포함 데이터 ===")
print(run_sql("SELECT MD$NUMBER FROM HDEL_DEFAULT.BLOCKNO$SF WHERE UPPER(MD$NUMBER) LIKE '%A101A%'"))

print("\n=== 5. BLOCKNO$SF에서 A101 또는 101 포함 데이터 ===")
print(run_sql("SELECT MD$NUMBER FROM HDEL_DEFAULT.BLOCKNO$SF WHERE UPPER(MD$NUMBER) LIKE '%A101%'"))

