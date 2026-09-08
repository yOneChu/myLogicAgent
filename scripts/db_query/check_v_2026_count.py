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

# 1. 2026년 등록일(MD$CDATE) 기준 V% 호기 개수 및 상태별 distribution
sql1 = """
WITH ouid AS (
    SELECT A.vf$ouid AS VFOID, A.MD$NUMBER AS HOGI, A.MD$STATUS, A.MD$CDATE, A.MD$MDATE
      FROM HDEL_DEFAULT.product$vf A, HDEL_DEFAULT.product$id B
     WHERE A.vf$identity = B.id$ouid
       AND A.vf$ouid     = B.id$wip
       AND A.MD$NUMBER NOT LIKE 'TEST%'
       AND A.MD$NUMBER NOT LIKE 'Q%'
       AND A.MD$NUMBER LIKE 'V%'
       AND SUBSTR(A.MD$CDATE, 1, 4) = '2026'
)
SELECT MD$STATUS, COUNT(*) AS PROD_CNT
  FROM ouid
 GROUP BY MD$STATUS
"""
print("1. 2026년 등록일 기준 V% 호기 (상태별):", test_query(sql1))

# 2. 2026년 등록일 기준 V% 호기 BOM 전체 건수 및 호기 수
sql2 = """
WITH ouid AS (
    SELECT A.vf$ouid AS VFOID, A.MD$NUMBER AS HOGI
      FROM HDEL_DEFAULT.product$vf A, HDEL_DEFAULT.product$id B
     WHERE A.vf$identity = B.id$ouid
       AND A.vf$ouid     = B.id$wip
       AND A.MD$NUMBER NOT LIKE 'TEST%'
       AND A.MD$NUMBER NOT LIKE 'Q%'
       AND A.MD$NUMBER LIKE 'V%'
       AND SUBSTR(A.MD$CDATE, 1, 4) = '2026'
)
SELECT COUNT(DISTINCT PE.PRODUCTOUID) AS HOGI_CNT, COUNT(*) AS TOTAL_BOM_ROWS
  FROM HDEL_DEFAULT.PARTOFEBOM PE
 INNER JOIN HDEL_DEFAULT.NORMALPART$VF NP ON PE.PARTOUID = NP.VF$OUID
 WHERE PE.PRODUCTOUID IN (SELECT VFOID FROM ouid)
"""
print("2. 2026년 등록일 기준 V% 호기 BOM 전체 건수:", test_query(sql2))
