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

# B181B 사용 호기들의 유효버전(WIP) 기준 연도별 분포 (RLS 상태)
sql_years_rls = """
WITH ouid AS (
    SELECT A.vf$ouid AS VFOID,
           A.MD$NUMBER AS HOGI,
           SUBSTR(A.MD$MDATE, 1, 4) AS MOD_YEAR
      FROM HDEL_DEFAULT.product$vf A, HDEL_DEFAULT.product$id B
     WHERE A.vf$identity = B.id$ouid
       AND A.vf$ouid     = B.id$wip
       AND A.MD$NUMBER NOT LIKE 'TEST%'
       AND A.MD$NUMBER NOT LIKE 'Q%'
       AND A.MD$STATUS = 'RLS'
)
SELECT O.MOD_YEAR, COUNT(DISTINCT PE.PRODUCTOUID) AS HOGI_CNT, COUNT(*) AS BOM_ROW_CNT
  FROM HDEL_DEFAULT.PARTOFEBOM PE
 INNER JOIN HDEL_DEFAULT.NORMALPART$VF NP ON PE.PARTOUID = NP.VF$OUID
 INNER JOIN ouid O ON PE.PRODUCTOUID = O.VFOID
 WHERE NP.BLOCKNO LIKE '%8613724a%'
 GROUP BY O.MOD_YEAR
 ORDER BY O.MOD_YEAR DESC
"""
print("B181B RLS Products Year Summary:", test_query(sql_years_rls))
