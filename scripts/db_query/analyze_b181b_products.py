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

# 1. B181B 자재를 사용하는 전체 호기 정보 (연도, 상태, 호기수)
sql_dist = """
WITH ouid AS (
    SELECT A.vf$ouid AS VFOID,
           A.MD$NUMBER AS HOGI,
           A.MD$STATUS AS STATUS,
           SUBSTR(A.MD$MDATE, 1, 4) AS MOD_YEAR,
           SUBSTR(A.MD$CDATE, 1, 4) AS CRE_YEAR
      FROM HDEL_DEFAULT.product$vf A, HDEL_DEFAULT.product$id B
     WHERE A.vf$identity = B.id$ouid
       AND A.vf$ouid     = B.id$wip
       AND A.MD$NUMBER NOT LIKE 'TEST%'
       AND A.MD$NUMBER NOT LIKE 'Q%'
)
SELECT O.MOD_YEAR, O.CRE_YEAR, O.STATUS, COUNT(DISTINCT PE.PRODUCTOUID) AS HOGI_CNT, COUNT(*) AS BOM_CNT
  FROM HDEL_DEFAULT.PARTOFEBOM PE
 INNER JOIN HDEL_DEFAULT.NORMALPART$VF NP ON PE.PARTOUID = NP.VF$OUID
 INNER JOIN ouid O ON PE.PRODUCTOUID = O.VFOID
 WHERE (SELECT MD$NUMBER FROM HDEL_DEFAULT.BLOCKNO$SF
         WHERE SF$OUID = DECODE(NP.BLOCKNO, NULL, NULL, TO_NUMBER(UPPER(SUBSTR(NP.BLOCKNO, 12)), 'XXXXXXXX'))) = 'B181B'
 GROUP BY O.MOD_YEAR, O.CRE_YEAR, O.STATUS
 ORDER BY O.MOD_YEAR DESC, O.CRE_YEAR DESC, O.STATUS
"""
print("Distribution of B181B products:", test_query(sql_dist))

# 2. COD 함수 없이 EL_ABRAND 확인해보는 테스트
sql_brand_test = """
WITH ouid AS (
    SELECT A.vf$ouid AS VFOID, A.MD$NUMBER AS HOGI, A.MD$STATUS, SUBSTR(A.MD$MDATE, 1, 4) AS MOD_YEAR
      FROM HDEL_DEFAULT.product$vf A, HDEL_DEFAULT.product$id B
     WHERE A.vf$identity = B.id$ouid
       AND A.vf$ouid     = B.id$wip
       AND A.MD$NUMBER NOT LIKE 'TEST%'
       AND A.MD$NUMBER NOT LIKE 'Q%'
)
SELECT O.HOGI, O.MOD_YEAR, O.MD$STATUS,
       (SELECT E.EL_ABRAND FROM HDEL_DEFAULT.ELV_INFO$ID A, HDEL_DEFAULT.ELV_INFO$VF E
         WHERE A.ID$OUID = E.VF$IDENTITY AND E.vf$ouid = A.id$wip AND E.MD$NUMBER = O.HOGI) AS RAW_BRAND,
       (SELECT HDEL_DEFAULT.COD(E.EL_ABRAND) FROM HDEL_DEFAULT.ELV_INFO$ID A, HDEL_DEFAULT.ELV_INFO$VF E
         WHERE A.ID$OUID = E.VF$IDENTITY AND E.vf$ouid = A.id$wip AND E.MD$NUMBER = O.HOGI) AS COD_BRAND
  FROM HDEL_DEFAULT.PARTOFEBOM PE
 INNER JOIN HDEL_DEFAULT.NORMALPART$VF NP ON PE.PARTOUID = NP.VF$OUID
 INNER JOIN ouid O ON PE.PRODUCTOUID = O.VFOID
 WHERE (SELECT MD$NUMBER FROM HDEL_DEFAULT.BLOCKNO$SF
         WHERE SF$OUID = DECODE(NP.BLOCKNO, NULL, NULL, TO_NUMBER(UPPER(SUBSTR(NP.BLOCKNO, 12)), 'XXXXXXXX'))) = 'B181B'
   AND ROWNUM <= 10
"""
print("Sample B181B products & brands:", test_query(sql_brand_test))
