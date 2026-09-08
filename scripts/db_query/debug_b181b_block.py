import json
import urllib.parse
import urllib.request
import ssl

API_URL = "https://vault-in.hdel.co.kr:8070/api/executeQuery"
API_KEY = "subae"

def test_query(sql):
    query_string = urllib.parse.urlencode({"key": API_KEY, "sql": sql})
    url = f"{API_URL}?{query_string}"
    req = urllib.request.Request(url, headers={"Accept": "application/json"})
    context = ssl._create_unverified_context()
    with urllib.request.urlopen(req, context=context) as resp:
        data = json.loads(resp.read().decode('utf-8'))
        return data

# 1. NORMALPART$VF BLOCKNO 샘플
sql1 = "SELECT MD$NUMBER, BLOCKNO, UPPERBLOCKNO FROM HDEL_DEFAULT.NORMALPART$VF WHERE BLOCKNO IS NOT NULL AND ROWNUM <= 10"
print("NP BLOCKNO sample:", test_query(sql1))

# 2. BLOCKNO$SF 의 B181B 의 SF$OUID 가져오기
sql2 = "SELECT SF$OUID, MD$NUMBER FROM HDEL_DEFAULT.BLOCKNO$SF WHERE MD$NUMBER = 'B181B'"
sf_b181b = test_query(sql2)
print("B181B SF OUID:", sf_b181b)

if sf_b181b:
    ouid_val = sf_b181b[0]['SF$OUID']
    # 16진수 변환
    hex_val = hex(int(ouid_val))[2:].upper()
    print(f"Dec OUID: {ouid_val}, Hex OUID: {hex_val}")
    
    # NP.BLOCKNO에 이 hex_val이 포함된 자재 찾기
    sql3 = f"SELECT MD$NUMBER, MD$DESC, BLOCKNO FROM HDEL_DEFAULT.NORMALPART$VF WHERE BLOCKNO LIKE '%{hex_val}%' OR UPPER(BLOCKNO) LIKE '%{hex_val}%'"
    print("Found parts with hex OUID:", test_query(sql3))
