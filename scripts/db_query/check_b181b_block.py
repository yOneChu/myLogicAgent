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

# 1. BLOCKNO$SF 테이블에서 B181B 관련 데이터 검색
sql_block = "SELECT SF$OUID, MD$NUMBER, COD(BLOCK_OPT) AS OPT FROM BLOCKNO$SF WHERE UPPER(MD$NUMBER) LIKE '%B181%'"
print("Block check:", test_query(sql_block))

# 2. NORMALPART$VF 에서 BLOCKNO 값 예시 확인
sql_part = "SELECT MD$NUMBER, SPEC, BLOCKNO FROM NORMALPART$VF WHERE UPPER(SPEC) LIKE '%B181B%' OR UPPER(MD$DESC) LIKE '%B181B%' AND ROWNUM <= 10"
print("Part check:", test_query(sql_part))

# 3. NORMALPART$VF에서 HEXTODEC 변환 후 BLOCKNO$SF와 연결되는 B181B 조사
sql_part2 = """
SELECT NP.MD$NUMBER, NP.MD$DESC, B.MD$NUMBER AS BLOCK_NO
  FROM NORMALPART$VF NP
 INNER JOIN BLOCKNO$SF B
    ON B.SF$OUID = DECODE(NP.BLOCKNO, NULL, NULL, HEXTODEC(UPPER(SUBSTR(NP.BLOCKNO, 12))))
 WHERE B.MD$NUMBER LIKE '%B181%' AND ROWNUM <= 10
"""
print("Part-Block Join check:", test_query(sql_part2))
