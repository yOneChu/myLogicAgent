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

# 1. BLOCKNO$SF 샘플
print("BLOCKNO Sample:", test_query("SELECT SF$OUID, MD$NUMBER FROM BLOCKNO$SF WHERE ROWNUM <= 20"))

# 2. B18 관련 블록 검색
print("B18 search:", test_query("SELECT SF$OUID, MD$NUMBER FROM BLOCKNO$SF WHERE UPPER(MD$NUMBER) LIKE '%181%'"))

# 3. NORMALPART$VF 의 BLOCKNO에서 HEXTODEC(UPPER(SUBSTR(NP.BLOCKNO, 12))) 한 결과값들 샘플
print("NP Block join sample:", test_query("""
SELECT B.MD$NUMBER, COUNT(*) AS CNT
  FROM NORMALPART$VF NP
 INNER JOIN BLOCKNO$SF B
    ON B.SF$OUID = DECODE(NP.BLOCKNO, NULL, NULL, HEXTODEC(UPPER(SUBSTR(NP.BLOCKNO, 12))))
 GROUP BY B.MD$NUMBER
 HAVING UPPER(B.MD$NUMBER) LIKE '%181%'
"""))
