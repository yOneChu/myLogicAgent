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

# B181B 자재 사용 제품(호기)들의 연도/상태 분포 조사 (연도 필터 없이)
sql_all_years = """
WITH b181b_parts AS (
    SELECT NP.VF$OUID
      FROM HDEL_DEFAULT.NORMALPART$VF NP
     WHERE (SELECT MD$NUMBER FROM HDEL_DEFAULT.BLOCKNO$SF
             WHERE SF$OUID = DECODE(NP.BLOCKNO, NULL, NULL, TO_NUMBER(UPPER(SUBSTR(NP.BLOCKNO, 12)), 'XXXXXXXX'))) = 'B181B'
)
SELECT SUBSTR(A.MD$MDATE, 1, 4) AS MOD_YEAR,
       SUBSTR(A.MD$CDATE, 1, 4) AS CRE_YEAR,
       A.MD$STATUS AS STATUS,
       COUNT(DISTINCT PE.PRODUCTOUID) AS HOGI_CNT
  FROM HDEL_DEFAULT.PARTOFEBOM PE
 INNER JOIN b181b_parts BP ON PE.PARTOUID = BP.VF$OUID
 INNER JOIN HDEL_DEFAULT.product$vf A ON PE.PRODUCTOUID = A.vf$ouid
 INNER JOIN HDEL_DEFAULT.product$id B ON A.vf$identity = B.id$ouid AND A.vf$ouid = B.id$wip
 WHERE A.MD$NUMBER NOT LIKE 'TEST%'
   AND A.MD$NUMBER NOT LIKE 'Q%'
 GROUP BY SUBSTR(A.MD$MDATE, 1, 4), SUBSTR(A.MD$CDATE, 1, 4), A.MD$STATUS
 ORDER BY MOD_YEAR DESC, CRE_YEAR DESC
"""
print("B181B product year distribution:", test_query(sql_all_years))
