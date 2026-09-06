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

# Test A: HDEL_DEFAULT.HEXTODEC 테스트
print("A. HDEL_DEFAULT.HEXTODEC 테스트:")
qA = "SELECT HDEL_DEFAULT.HEXTODEC('1A') AS DEC_VAL FROM DUAL"
print(run_sql(qA))

# Test B: NORMALPART$VF의 BLOCKNO 값 샘플
print("\nB. NORMALPART$VF 의 BLOCKNO 샘플 5건:")
qB = "SELECT VF$OUID, MD$NUMBER, BLOCKNO FROM HDEL_DEFAULT.NORMALPART$VF WHERE BLOCKNO IS NOT NULL AND ROWNUM <= 5"
print(run_sql(qB))

# Test C: BLOCKNO$SF 의 OUID 및 MD$NUMBER 샘플 5건
print("\nC. BLOCKNO$SF 의 SF$OUID 샘플 5건:")
qC = "SELECT SF$OUID, MD$NUMBER FROM HDEL_DEFAULT.BLOCKNO$SF WHERE ROWNUM <= 5"
print(run_sql(qC))
