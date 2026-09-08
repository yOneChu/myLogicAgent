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

# 1. 2026년 릴리즈(RLS) 제품 중 B181B 브랜드별 현장 통계
sql_brand_summary = """
WITH ouid AS (
    SELECT A.vf$ouid AS VFOID,
           A.MD$NUMBER AS HOGI
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
     WHERE NP.BLOCKNO LIKE '%8613724a%'
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
brand_stats = test_query(sql_brand_summary)
print("1. Brand Summary Stats:")
for b in brand_stats:
    print(b)

# 2. 브랜드별 + 기종(GISONG)별 세부 통계
sql_brand_gisong = """
WITH ouid AS (
    SELECT A.vf$ouid AS VFOID,
           A.MD$NUMBER AS HOGI
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
     WHERE NP.BLOCKNO LIKE '%8613724a%'
)
SELECT NVL(
         (SELECT HDEL_DEFAULT.COD(E.EL_ABRAND) FROM HDEL_DEFAULT.ELV_INFO$ID A, HDEL_DEFAULT.ELV_INFO$VF E
           WHERE A.ID$OUID = E.VF$IDENTITY AND E.vf$ouid = A.id$wip AND E.MD$NUMBER = O.HOGI),
         '미지정'
       ) AS BRAND,
       NVL(
         (SELECT HDEL_DEFAULT.COD(E.EL_ATYP) FROM HDEL_DEFAULT.ELV_INFO$ID A, HDEL_DEFAULT.ELV_INFO$VF E
           WHERE A.ID$OUID = E.VF$IDENTITY AND E.vf$ouid = A.id$wip AND E.MD$NUMBER = O.HOGI),
         '미지정'
       ) AS GISONG,
       COUNT(DISTINCT PE.PRODUCTOUID) AS HOGI_CNT,
       COUNT(*) AS BOM_ROW_CNT
  FROM HDEL_DEFAULT.PARTOFEBOM PE
 INNER JOIN b181b_parts BP ON PE.PARTOUID = BP.VF$OUID
 INNER JOIN ouid O ON PE.PRODUCTOUID = O.VFOID
 GROUP BY (SELECT HDEL_DEFAULT.COD(E.EL_ABRAND) FROM HDEL_DEFAULT.ELV_INFO$ID A, HDEL_DEFAULT.ELV_INFO$VF E
            WHERE A.ID$OUID = E.VF$IDENTITY AND E.vf$ouid = A.id$wip AND E.MD$NUMBER = O.HOGI),
          (SELECT HDEL_DEFAULT.COD(E.EL_ATYP) FROM HDEL_DEFAULT.ELV_INFO$ID A, HDEL_DEFAULT.ELV_INFO$VF E
            WHERE A.ID$OUID = E.VF$IDENTITY AND E.vf$ouid = A.id$wip AND E.MD$NUMBER = O.HOGI)
 ORDER BY BRAND, HOGI_CNT DESC
"""
gisong_stats = test_query(sql_brand_gisong)
print("\n2. Brand + Gisong Breakdown Sample:")
for g in gisong_stats[:15]:
    print(g)

# 3. B181B 블록 내 최다 사용 자재 TOP 5
sql_top_parts = """
WITH ouid AS (
    SELECT A.vf$ouid AS VFOID
      FROM HDEL_DEFAULT.product$vf A, HDEL_DEFAULT.product$id B
     WHERE A.vf$identity = B.id$ouid
       AND A.vf$ouid     = B.id$wip
       AND A.MD$NUMBER NOT LIKE 'TEST%'
       AND A.MD$NUMBER NOT LIKE 'Q%'
       AND SUBSTR(A.MD$MDATE, 1, 4) = '2026'
       AND A.MD$STATUS = 'RLS'
),
b181b_parts AS (
    SELECT NP.VF$OUID, NP.MD$NUMBER AS PARTNO, NP.MD$DESC AS PARTNAME, NVL(NP.SPEC, '') AS SPEC
      FROM HDEL_DEFAULT.NORMALPART$VF NP
     WHERE NP.BLOCKNO LIKE '%8613724a%'
)
SELECT BP.PARTNO, BP.PARTNAME, BP.SPEC, COUNT(DISTINCT PE.PRODUCTOUID) AS HOGI_CNT, COUNT(*) AS TOTAL_BOM_QTY
  FROM HDEL_DEFAULT.PARTOFEBOM PE
 INNER JOIN b181b_parts BP ON PE.PARTOUID = BP.VF$OUID
 INNER JOIN ouid O ON PE.PRODUCTOUID = O.VFOID
 GROUP BY BP.PARTNO, BP.PARTNAME, BP.SPEC
 ORDER BY HOGI_CNT DESC
"""
top_parts = test_query(sql_top_parts)
print("\n3. Top Parts in B181B (2026):")
for p in top_parts[:10]:
    print(p)
