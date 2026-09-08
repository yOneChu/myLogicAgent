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

# Test 1: Direct join with BLOCKNO$SF
sql1 = """
SELECT NP.MD$NUMBER, NP.MD$DESC, B.MD$NUMBER AS BLOCK_NO
  FROM HDEL_DEFAULT.NORMALPART$VF NP
 INNER JOIN HDEL_DEFAULT.BLOCKNO$SF B
    ON B.SF$OUID = DECODE(NP.BLOCKNO, NULL, NULL, HEXTODEC(UPPER(SUBSTR(NP.BLOCKNO, 12))))
 WHERE B.MD$NUMBER = 'B181B' AND ROWNUM <= 10
"""
print("Test 1 Direct Join B181B Parts:", test_query(sql1))

# Test 2: BOM join with B181B Parts
sql2 = """
WITH ouid AS (
    SELECT A.vf$ouid AS VFOID
      FROM HDEL_DEFAULT.product$vf A, HDEL_DEFAULT.product$id B
     WHERE A.vf$identity = B.id$ouid
       AND A.vf$ouid     = B.id$wip
       AND A.MD$NUMBER NOT LIKE 'TEST%'
       AND A.MD$NUMBER NOT LIKE 'Q%'
       AND SUBSTR(A.MD$MDATE, 1, 4) = '2026'
       AND A.MD$STATUS = 'RLS'
)
SELECT COUNT(DISTINCT PE.PRODUCTOUID) AS HOGI_CNT, COUNT(*) AS TOTAL_BOM_ROWS
  FROM HDEL_DEFAULT.PARTOFEBOM PE
 INNER JOIN HDEL_DEFAULT.NORMALPART$VF NP ON PE.PARTOUID = NP.VF$OUID
 INNER JOIN HDEL_DEFAULT.BLOCKNO$SF B ON B.SF$OUID = DECODE(NP.BLOCKNO, NULL, NULL, HEXTODEC(UPPER(SUBSTR(NP.BLOCKNO, 12))))
 WHERE PE.PRODUCTOUID IN (SELECT VFOID FROM ouid)
   AND B.MD$NUMBER = 'B181B'
"""
print("Test 2 2026 RLS BOM Count for B181B:", test_query(sql2))

# Test 3: Check years of products using B181B
sql3 = """
WITH ouid AS (
    SELECT A.vf$ouid AS VFOID, A.MD$NUMBER, A.MD$STATUS, SUBSTR(A.MD$MDATE, 1, 4) AS MOD_YEAR
      FROM HDEL_DEFAULT.product$vf A, HDEL_DEFAULT.product$id B
     WHERE A.vf$identity = B.id$ouid
       AND A.vf$ouid     = B.id$wip
       AND A.MD$NUMBER NOT LIKE 'TEST%'
       AND A.MD$NUMBER NOT LIKE 'Q%'
)
SELECT P.MOD_YEAR, P.MD$STATUS, COUNT(DISTINCT PE.PRODUCTOUID) AS HOGI_CNT
  FROM HDEL_DEFAULT.PARTOFEBOM PE
 INNER JOIN HDEL_DEFAULT.NORMALPART$VF NP ON PE.PARTOUID = NP.VF$OUID
 INNER JOIN HDEL_DEFAULT.BLOCKNO$SF B ON B.SF$OUID = DECODE(NP.BLOCKNO, NULL, NULL, HEXTODEC(UPPER(SUBSTR(NP.BLOCKNO, 12))))
 INNER JOIN ouid P ON PE.PRODUCTOUID = P.VFOID
 WHERE B.MD$NUMBER = 'B181B'
 GROUP BY P.MOD_YEAR, P.MD$STATUS
 ORDER BY P.MOD_YEAR DESC, P.MD$STATUS
"""
print("Test 3 All Years distribution for B181B:", test_query(sql3))
