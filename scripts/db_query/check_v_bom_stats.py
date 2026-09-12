import json
import urllib.parse
import urllib.request
import ssl

API_URL = "https://vault-in.hdel.co.kr:8070/api/executeQuery"
API_KEY = "subae"

def run_sql(sql):
    query_string = urllib.parse.urlencode({"key": API_KEY, "sql": sql})
    url = f"{API_URL}?{query_string}"
    req = urllib.request.Request(url, headers={"Accept": "application/json"})
    context = ssl._create_unverified_context()
    with urllib.request.urlopen(req, context=context) as resp:
        return json.loads(resp.read().decode('utf-8'))

# 1. 전체 V호기 (265개 호기) BOM 행 수 및 고유 부품 수
sql_total_bom = """
WITH ouid AS (
    SELECT A.vf$ouid AS VFOID
      FROM HDEL_DEFAULT.product$vf A, HDEL_DEFAULT.product$id B
     WHERE A.vf$identity = B.id$ouid
       AND A.vf$ouid     = B.id$wip
       AND A.MD$NUMBER NOT LIKE 'TEST%'
       AND A.MD$NUMBER NOT LIKE 'Q%'
       AND A.MD$NUMBER LIKE 'V%'
)
SELECT 
    COUNT(DISTINCT PE.PRODUCTOUID) AS HOGI_COUNT,
    COUNT(DISTINCT NP.MD$NUMBER) AS PART_COUNT,
    COUNT(*) AS TOTAL_BOM_ROWS
  FROM HDEL_DEFAULT.PARTOFEBOM PE
 INNER JOIN HDEL_DEFAULT.NORMALPART$VF NP ON PE.PARTOUID = NP.VF$OUID
 WHERE PE.PRODUCTOUID IN (SELECT VFOID FROM ouid)
"""

# 2. 2026년 수정/등록 V호기 BOM 행 수
sql_2026_bom = """
WITH ouid AS (
    SELECT A.vf$ouid AS VFOID
      FROM HDEL_DEFAULT.product$vf A, HDEL_DEFAULT.product$id B
     WHERE A.vf$identity = B.id$ouid
       AND A.vf$ouid     = B.id$wip
       AND A.MD$NUMBER NOT LIKE 'TEST%'
       AND A.MD$NUMBER NOT LIKE 'Q%'
       AND A.MD$NUMBER LIKE 'V%'
       AND SUBSTR(A.MD$MDATE, 1, 4) = '2026'
)
SELECT 
    COUNT(DISTINCT PE.PRODUCTOUID) AS HOGI_COUNT,
    COUNT(DISTINCT NP.MD$NUMBER) AS PART_COUNT,
    COUNT(*) AS TOTAL_BOM_ROWS
  FROM HDEL_DEFAULT.PARTOFEBOM PE
 INNER JOIN HDEL_DEFAULT.NORMALPART$VF NP ON PE.PARTOUID = NP.VF$OUID
 WHERE PE.PRODUCTOUID IN (SELECT VFOID FROM ouid)
"""

# 3. 2026년 RLS(릴리즈) V호기 BOM 행 수
sql_2026_rls_bom = """
WITH ouid AS (
    SELECT A.vf$ouid AS VFOID
      FROM HDEL_DEFAULT.product$vf A, HDEL_DEFAULT.product$id B
     WHERE A.vf$identity = B.id$ouid
       AND A.vf$ouid     = B.id$wip
       AND A.MD$NUMBER NOT LIKE 'TEST%'
       AND A.MD$NUMBER NOT LIKE 'Q%'
       AND A.MD$NUMBER LIKE 'V%'
       AND A.MD$STATUS = 'RLS'
       AND SUBSTR(A.MD$MDATE, 1, 4) = '2026'
)
SELECT 
    COUNT(DISTINCT PE.PRODUCTOUID) AS HOGI_COUNT,
    COUNT(DISTINCT NP.MD$NUMBER) AS PART_COUNT,
    COUNT(*) AS TOTAL_BOM_ROWS
  FROM HDEL_DEFAULT.PARTOFEBOM PE
 INNER JOIN HDEL_DEFAULT.NORMALPART$VF NP ON PE.PARTOUID = NP.VF$OUID
 WHERE PE.PRODUCTOUID IN (SELECT VFOID FROM ouid)
"""

print("=== 1. 전체 V호기 (265개 호기) BOM 통계 ===")
print(run_sql(sql_total_bom))

print("\n=== 2. 2026년 V호기 (92개 호기) BOM 통계 ===")
print(run_sql(sql_2026_bom))

print("\n=== 3. 2026년 RLS(릴리즈) V호기 (71개 호기) BOM 통계 ===")
print(run_sql(sql_2026_rls_bom))
