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

# 1. 2026년 릴리즈(RLS) 제품 중 B181B 브랜드별 현장 수 집계
sql_brand = """
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
),
hogi_b181b AS (
    SELECT DISTINCT PE.PRODUCTOUID AS VFOID, O.HOGI
      FROM HDEL_DEFAULT.PARTOFEBOM PE
     INNER JOIN b181b_parts BP ON PE.PARTOUID = BP.VF$OUID
     INNER JOIN ouid O ON PE.PRODUCTOUID = O.VFOID
),
hogi_elv AS (
    SELECT E.MD$NUMBER AS HOGI,
           HDEL_DEFAULT.COD(E.EL_ABRAND) AS BRAND
      FROM HDEL_DEFAULT.ELV_INFO$ID A, HDEL_DEFAULT.ELV_INFO$VF E
     WHERE A.ID$OUID = E.VF$IDENTITY AND E.vf$ouid = A.id$wip
)
SELECT NVL(E.BRAND, '미지정') AS BRAND,
       COUNT(DISTINCT H.VFOID) AS HOGI_CNT
  FROM hogi_b181b H
  LEFT OUTER JOIN hogi_elv E ON H.HOGI = E.HOGI
 GROUP BY NVL(E.BRAND, '미지정')
 ORDER BY HOGI_CNT DESC
"""
brand_res = test_query(sql_brand)
print("=== 1. 2026 B181B 브랜드별 현장 수 ===")
for r in brand_res:
    print(r)

# 2. 브랜드 및 기종별 현장 수 세부 집계
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
),
hogi_b181b AS (
    SELECT DISTINCT PE.PRODUCTOUID AS VFOID, O.HOGI
      FROM HDEL_DEFAULT.PARTOFEBOM PE
     INNER JOIN b181b_parts BP ON PE.PARTOUID = BP.VF$OUID
     INNER JOIN ouid O ON PE.PRODUCTOUID = O.VFOID
),
hogi_elv AS (
    SELECT E.MD$NUMBER AS HOGI,
           HDEL_DEFAULT.COD(E.EL_ABRAND) AS BRAND,
           HDEL_DEFAULT.COD(E.EL_ATYP) AS GISONG
      FROM HDEL_DEFAULT.ELV_INFO$ID A, HDEL_DEFAULT.ELV_INFO$VF E
     WHERE A.ID$OUID = E.VF$IDENTITY AND E.vf$ouid = A.id$wip
)
SELECT NVL(E.BRAND, '미지정') AS BRAND,
       NVL(E.GISONG, '미지정') AS GISONG,
       COUNT(DISTINCT H.VFOID) AS HOGI_CNT
  FROM hogi_b181b H
  LEFT OUTER JOIN hogi_elv E ON H.HOGI = E.HOGI
 GROUP BY NVL(E.BRAND, '미지정'), NVL(E.GISONG, '미지정')
 ORDER BY BRAND, HOGI_CNT DESC
"""
gisong_res = test_query(sql_brand_gisong)
print("\n=== 2. 브랜드/기종별 세부 현장 수 ===")
for r in gisong_res:
    print(r)

# 3. B181B 블록의 주요 탑 적용 자재 TOP 10
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
SELECT BP.PARTNO, BP.PARTNAME, BP.SPEC, COUNT(DISTINCT PE.PRODUCTOUID) AS HOGI_CNT
  FROM HDEL_DEFAULT.PARTOFEBOM PE
 INNER JOIN b181b_parts BP ON PE.PARTOUID = BP.VF$OUID
 INNER JOIN ouid O ON PE.PRODUCTOUID = O.VFOID
 GROUP BY BP.PARTNO, BP.PARTNAME, BP.SPEC
 ORDER BY HOGI_CNT DESC
"""
top_parts_res = test_query(sql_top_parts)
print("\n=== 3. 2026 B181B 블록 최다 적용 자재 TOP 10 ===")
for r in top_parts_res[:10]:
    print(r)
