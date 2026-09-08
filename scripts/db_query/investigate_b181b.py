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

# Step 1. B181B 블럭을 사용하는 자재 수
sql_parts = """
SELECT NP.MD$NUMBER AS PARTNO, NP.MD$DESC AS PARTNAME
  FROM HDEL_DEFAULT.NORMALPART$VF NP
 WHERE (SELECT MD$NUMBER FROM HDEL_DEFAULT.BLOCKNO$SF
         WHERE SF$OUID = DECODE(NP.BLOCKNO, NULL, NULL, HEXTODEC(UPPER(SUBSTR(NP.BLOCKNO, 12))))) = 'B181B'
"""
parts = test_query(sql_parts)
print(f"Step 1. B181B Parts count: {len(parts)}")
if parts:
    print("Sample parts:", parts[:5])

# Step 2. B181B 블럭 자재가 BOM(PARTOFEBOM)에 사용된 전체 건수 및 제품 OID 수
sql_bom = """
SELECT COUNT(DISTINCT PE.PRODUCTOUID) AS HOGI_OID_CNT, COUNT(*) AS BOM_CNT
  FROM HDEL_DEFAULT.PARTOFEBOM PE
 INNER JOIN HDEL_DEFAULT.NORMALPART$VF NP ON PE.PARTOUID = NP.VF$OUID
 WHERE (SELECT MD$NUMBER FROM HDEL_DEFAULT.BLOCKNO$SF
         WHERE SF$OUID = DECODE(NP.BLOCKNO, NULL, NULL, HEXTODEC(UPPER(SUBSTR(NP.BLOCKNO, 12))))) = 'B181B'
"""
bom_res = test_query(sql_bom)
print("Step 2. BOM usage count:", bom_res)

# Step 3. B181B 자재가 사용된 제품(PRODUCT$VF) 연도별/상태별 분포
sql_prod_dist = """
WITH ouid AS (
    SELECT A.vf$ouid AS VFOID, A.MD$NUMBER AS HOGI, A.MD$STATUS, SUBSTR(A.MD$MDATE, 1, 4) AS MOD_YEAR, SUBSTR(A.MD$CDATE, 1, 4) AS CRE_YEAR
      FROM HDEL_DEFAULT.product$vf A, HDEL_DEFAULT.product$id B
     WHERE A.vf$identity = B.id$ouid
       AND A.vf$ouid     = B.id$wip
       AND A.MD$NUMBER NOT LIKE 'TEST%'
       AND A.MD$NUMBER NOT LIKE 'Q%'
)
SELECT P.MOD_YEAR, P.CRE_YEAR, P.MD$STATUS, COUNT(DISTINCT PE.PRODUCTOUID) AS HOGI_CNT
  FROM HDEL_DEFAULT.PARTOFEBOM PE
 INNER JOIN HDEL_DEFAULT.NORMALPART$VF NP ON PE.PARTOUID = NP.VF$OUID
 INNER JOIN ouid P ON PE.PRODUCTOUID = P.VFOID
 WHERE (SELECT MD$NUMBER FROM HDEL_DEFAULT.BLOCKNO$SF
         WHERE SF$OUID = DECODE(NP.BLOCKNO, NULL, NULL, HEXTODEC(UPPER(SUBSTR(NP.BLOCKNO, 12))))) = 'B181B'
 GROUP BY P.MOD_YEAR, P.CRE_YEAR, P.MD$STATUS
 ORDER BY P.MOD_YEAR DESC, P.MD$STATUS
"""
dist_res = test_query(sql_prod_dist)
print("Step 3. Product Distribution:", dist_res)
