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

# 1. 2026년 릴리즈(RLS) 제품 중 B181B 사용 현장 브랜드 통계
sql_rls = """
WITH ouid AS (
    SELECT A.vf$ouid AS VFOID, A.MD$NUMBER AS HOGI
      FROM HDEL_DEFAULT.product$vf A, HDEL_DEFAULT.product$id B
     WHERE A.vf$identity = B.id$ouid
       AND A.vf$ouid     = B.id$wip
       AND A.MD$NUMBER NOT LIKE 'TEST%'
       AND A.MD$NUMBER NOT LIKE 'Q%'
       AND SUBSTR(A.MD$MDATE, 1, 4) = '2026'
       AND A.MD$STATUS = 'RLS'
),
b181b_parts AS (
    SELECT NP.VF$OUID
      FROM HDEL_DEFAULT.NORMALPART$VF NP
     WHERE (SELECT MD$NUMBER FROM HDEL_DEFAULT.BLOCKNO$SF
             WHERE SF$OUID = DECODE(NP.BLOCKNO, NULL, NULL, TO_NUMBER(UPPER(SUBSTR(NP.BLOCKNO, 12)), 'XXXXXXXX'))) = 'B181B'
)
SELECT NVL(
         (SELECT HDEL_DEFAULT.COD(E.EL_ABRAND) FROM HDEL_DEFAULT.ELV_INFO$ID A, HDEL_DEFAULT.ELV_INFO$VF E
           WHERE A.ID$OUID = E.VF$IDENTITY AND E.vf$ouid = A.id$wip AND E.MD$NUMBER = O.HOGI),
         '미지정'
       ) AS BRAND,
       COUNT(DISTINCT PE.PRODUCTOUID) AS HOGI_CNT,
       COUNT(*) AS BOM_ROW_CNT
  FROM HDEL_DEFAULT.PARTOFEBOM PE
 INNER JOIN b181b_parts BP ON PE.PARTOUID = BP.VF$OUID
 INNER JOIN ouid O ON PE.PRODUCTOUID = O.VFOID
 GROUP BY (SELECT HDEL_DEFAULT.COD(E.EL_ABRAND) FROM HDEL_DEFAULT.ELV_INFO$ID A, HDEL_DEFAULT.ELV_INFO$VF E
            WHERE A.ID$OUID = E.VF$IDENTITY AND E.vf$ouid = A.id$wip AND E.MD$NUMBER = O.HOGI)
 ORDER BY HOGI_CNT DESC
"""
print("1. RLS 2026 Summary:", test_query(sql_rls))

# 2. 2026년 전체(상태 미제한) 제품 중 B181B 사용 현장 브랜드/상태 통계
sql_all_2026 = """
WITH ouid AS (
    SELECT A.vf$ouid AS VFOID, A.MD$NUMBER AS HOGI, A.MD$STATUS AS STATUS
      FROM HDEL_DEFAULT.product$vf A, HDEL_DEFAULT.product$id B
     WHERE A.vf$identity = B.id$ouid
       AND A.vf$ouid     = B.id$wip
       AND A.MD$NUMBER NOT LIKE 'TEST%'
       AND A.MD$NUMBER NOT LIKE 'Q%'
       AND SUBSTR(A.MD$MDATE, 1, 4) = '2026'
),
b181b_parts AS (
    SELECT NP.VF$OUID
      FROM HDEL_DEFAULT.NORMALPART$VF NP
     WHERE (SELECT MD$NUMBER FROM HDEL_DEFAULT.BLOCKNO$SF
             WHERE SF$OUID = DECODE(NP.BLOCKNO, NULL, NULL, TO_NUMBER(UPPER(SUBSTR(NP.BLOCKNO, 12)), 'XXXXXXXX'))) = 'B181B'
)
SELECT O.STATUS,
       NVL(
         (SELECT HDEL_DEFAULT.COD(E.EL_ABRAND) FROM HDEL_DEFAULT.ELV_INFO$ID A, HDEL_DEFAULT.ELV_INFO$VF E
           WHERE A.ID$OUID = E.VF$IDENTITY AND E.vf$ouid = A.id$wip AND E.MD$NUMBER = O.HOGI),
         '미지정'
       ) AS BRAND,
       COUNT(DISTINCT PE.PRODUCTOUID) AS HOGI_CNT,
       COUNT(*) AS BOM_ROW_CNT
  FROM HDEL_DEFAULT.PARTOFEBOM PE
 INNER JOIN b181b_parts BP ON PE.PARTOUID = BP.VF$OUID
 INNER JOIN ouid O ON PE.PRODUCTOUID = O.VFOID
 GROUP BY O.STATUS,
          (SELECT HDEL_DEFAULT.COD(E.EL_ABRAND) FROM HDEL_DEFAULT.ELV_INFO$ID A, HDEL_DEFAULT.ELV_INFO$VF E
            WHERE A.ID$OUID = E.VF$IDENTITY AND E.vf$ouid = A.id$wip AND E.MD$NUMBER = O.HOGI)
 ORDER BY O.STATUS, HOGI_CNT DESC
"""
print("2. All 2026 Summary:", test_query(sql_all_2026))
