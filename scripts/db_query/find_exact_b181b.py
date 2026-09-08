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

# B181B OUID
res = test_query("SELECT SF$OUID, MD$NUMBER FROM HDEL_DEFAULT.BLOCKNO$SF WHERE MD$NUMBER = 'B181B'")
print("B181B row:", res)

if res:
    ouid = res[0]['SF$OUID']
    hex_str = hex(int(ouid))[2:].lower()
    print(f"OUID: {ouid}, Hex: {hex_str}")
    
    # NP.BLOCKNO 에서 이 OUID 찾아보기
    sql_np = f"SELECT MD$NUMBER, MD$DESC, BLOCKNO FROM HDEL_DEFAULT.NORMALPART$VF WHERE BLOCKNO LIKE '%{hex_str}%'"
    parts = test_query(sql_np)
    print(f"Parts matching {hex_str}: {len(parts)}")
    if parts:
        print("Sample:", parts[:3])
