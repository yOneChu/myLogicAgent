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
        print(f"SQL: {sql[:100]}...")
        print(f"Count: {len(data)}")
        if data:
            print("Sample:", data[0])

# 1. 2026년 수정된 호기 중 B181B 블록을 가진 호기 및 블록 정보 확인 (STATUS 제한 없이)
sql1 = """
WITH ouid AS (
    SELECT A.vf$ouid AS VFOID, A.MD$NUMBER, A.MD$STATUS, A.MD$MDATE
      FROM product$vf A, product$id B
     WHERE A.vf$identity = B.id$ouid
       AND A.vf$ouid     = B.id$wip
       AND A.MD$NUMBER NOT LIKE 'TEST%'
       AND A.MD$NUMBER NOT LIKE 'Q%'
       AND SUBSTR(A.MD$MDATE, 0, 4) = '2026'
)
SELECT COUNT(*) AS CNT
  FROM PARTOFEBOM PE
 INNER JOIN NORMALPART$VF NP ON PE.PARTOUID = NP.VF$OUID
 WHERE PE.PRODUCTOUID IN (SELECT VFOID FROM ouid)
   AND (SELECT MD$NUMBER FROM BLOCKNO$SF
         WHERE SF$OUID = DECODE(NP.BLOCKNO, NULL, NULL, HEXTODEC(UPPER(SUBSTR(NP.BLOCKNO, 12))))) = 'B181B'
"""

# 2. 연도 상관없이 B181B 블록 사용 건수 확인
sql2 = """
SELECT COUNT(DISTINCT PE.PRODUCTOUID) AS PROD_CNT, COUNT(*) AS TOTAL_CNT
  FROM PARTOFEBOM PE
 INNER JOIN NORMALPART$VF NP ON PE.PARTOUID = NP.VF$OUID
 WHERE (SELECT MD$NUMBER FROM BLOCKNO$SF
         WHERE SF$OUID = DECODE(NP.BLOCKNO, NULL, NULL, HEXTODEC(UPPER(SUBSTR(NP.BLOCKNO, 12))))) = 'B181B'
"""

print("Testing SQL 1...")
test_query(sql1)
print("\nTesting SQL 2...")
test_query(sql2)
