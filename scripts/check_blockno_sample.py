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

print("--- 1. NORMALPART$VF.BLOCKNO 샘플 20개 출력 ---")
sql1 = "SELECT MD$NUMBER, BLOCKNO FROM HDEL_DEFAULT.NORMALPART$VF WHERE BLOCKNO IS NOT NULL AND ROWNUM <= 20"
res1 = query(sql1)
for r in res1:
    print(r)

print("\n--- 2. HEXTODEC(UPPER(SUBSTR(BLOCKNO, 12))) 변환 샘플 ---")
sql2 = "SELECT BLOCKNO, SUBSTR(BLOCKNO, 12) AS SUB12, HEXTODEC(UPPER(SUBSTR(BLOCKNO, 12))) AS OUID_DEC FROM HDEL_DEFAULT.NORMALPART$VF WHERE BLOCKNO IS NOT NULL AND ROWNUM <= 10"
res2 = query(sql2)
for r in res2:
    print(r)

