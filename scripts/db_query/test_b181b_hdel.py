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

# 1. HDEL_DEFAULT.BLOCKNO$SF 에서 B181B 조회
sql1 = "SELECT SF$OUID, MD$NUMBER, COD(BLOCK_OPT) AS OPT FROM HDEL_DEFAULT.BLOCKNO$SF WHERE UPPER(MD$NUMBER) LIKE '%B181%'"
print("Block check:", test_query(sql1))

# 2. HDEL_DEFAULT 테이블들로 B181B 조인 건수 확인
sql2 = """
WITH ouid AS (
    SELECT A.vf$ouid AS VFOID
      FROM HDEL_DEFAULT.product$vf A, HDEL_DEFAULT.product$id B
     WHERE A.vf$identity = B.id$ouid
       AND A.vf$ouid     = B.id$wip
       AND A.MD$NUMBER NOT LIKE 'TEST%'
       AND A.MD$NUMBER NOT LIKE 'Q%'
       AND SUBSTR(A.MD$MDATE, 0, 4) = '2026'
       AND A.MD$STATUS = 'RLS'
)
SELECT NVL(
         (SELECT COD(E.EL_ABRAND) FROM HDEL_DEFAULT.ELV_INFO$ID A, HDEL_DEFAULT.ELV_INFO$VF E
           WHERE A.ID$OUID = E.VF$IDENTITY AND E.vf$ouid = A.id$wip
             AND E.MD$NUMBER = (SELECT F.MD$NUMBER FROM HDEL_DEFAULT.PRODUCT$VF F WHERE F.VF$OUID = PE.PRODUCTOUID)),
         '미지정'
       ) AS BRAND,
       COUNT(DISTINCT PE.PRODUCTOUID) AS HOGI_CNT,
       COUNT(*) AS BOM_ROW_CNT
  FROM HDEL_DEFAULT.PARTOFEBOM PE
 INNER JOIN HDEL_DEFAULT.NORMALPART$VF NP ON PE.PARTOUID = NP.VF$OUID
 WHERE PE.PRODUCTOUID IN (SELECT VFOID FROM ouid)
   AND (SELECT MD$NUMBER FROM HDEL_DEFAULT.BLOCKNO$SF
         WHERE SF$OUID = DECODE(NP.BLOCKNO, NULL, NULL, HEXTODEC(UPPER(SUBSTR(NP.BLOCKNO, 12))))) = 'B181B'
 GROUP BY (SELECT COD(E.EL_ABRAND) FROM HDEL_DEFAULT.ELV_INFO$ID A, HDEL_DEFAULT.ELV_INFO$VF E
            WHERE A.ID$OUID = E.VF$IDENTITY AND E.vf$ouid = A.id$wip
              AND E.MD$NUMBER = (SELECT F.MD$NUMBER FROM HDEL_DEFAULT.PRODUCT$VF F WHERE F.VF$OUID = PE.PRODUCTOUID))
 ORDER BY HOGI_CNT DESC
"""
print("Summary query result:", test_query(sql2))
