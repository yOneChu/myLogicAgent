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

# 명세서 11장 기본 SELECT 템플릿 사용
sql_test = """
WITH ouid AS (
    SELECT A.vf$ouid AS VFOID
      FROM HDEL_DEFAULT.product$vf A, HDEL_DEFAULT.product$id B
     WHERE A.vf$identity = B.id$ouid
       AND A.vf$ouid     = B.id$wip
       AND A.MD$NUMBER NOT LIKE 'TEST%'
       AND A.MD$NUMBER NOT LIKE 'Q%'
       AND A.MD$NUMBER LIKE 'V%'
)
SELECT (SELECT MD$NUMBER FROM HDEL_DEFAULT.PRODUCT$VF WHERE VF$OUID = PE.PRODUCTOUID) AS PARENTNO,
       (SELECT F.VF$VERSION FROM HDEL_DEFAULT.PRODUCT$VF F WHERE F.VF$OUID = PE.PRODUCTOUID) AS PARENT_VER,
       (SELECT PRODUCT.MD$STATUS FROM HDEL_DEFAULT.PRODUCT$VF PRODUCT WHERE PRODUCT.VF$OUID = PE.PRODUCTOUID) AS PROD_STATUS,
       NP.MD$NUMBER  AS PARTNO,
       NP.MD$DESC    AS PARTNAME,
       NP.VF$VERSION AS PART_VERSION,
       NVL(NP.SPEC, '') AS SPEC,
       NVL(NP.G_L_CODE, '') AS GLCODE,
       PE.QTY AS PART_QTY,
       PE.CMT AS CMT,
       (SELECT MD$NUMBER FROM HDEL_DEFAULT.BLOCKNO$SF WHERE SF$OUID = DECODE(NP.BLOCKNO, NULL, NULL, HDEL_DEFAULT.HEXTODEC(UPPER(SUBSTR(NP.BLOCKNO, 12))))) AS BLOCKNO
  FROM HDEL_DEFAULT.PARTOFEBOM PE
 INNER JOIN HDEL_DEFAULT.NORMALPART$VF NP ON PE.PARTOUID = NP.VF$OUID
 WHERE PE.PRODUCTOUID IN (SELECT VFOID FROM ouid)
   AND ROWNUM <= 5
"""

res = run_sql(sql_test)
print("Result count:", len(res))
print("Sample:", json.dumps(res, ensure_ascii=False, indent=2))
