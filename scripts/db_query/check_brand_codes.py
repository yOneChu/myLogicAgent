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

# 1. 2026년 B181B 제품 20개의 HOGI 번호 추출
sql_hogi = """
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
     WHERE NP.BLOCKNO LIKE '%8613724a%'
)
SELECT DISTINCT O.HOGI
  FROM HDEL_DEFAULT.PARTOFEBOM PE
 INNER JOIN b181b_parts BP ON PE.PARTOUID = BP.VF$OUID
 INNER JOIN ouid O ON PE.PRODUCTOUID = O.VFOID
 WHERE ROWNUM <= 20
"""
hogis = test_query(sql_hogi)
print("Sample Hogis (2026 B181B):", hogis)

if hogis:
    hogi_list = [h['HOGI'] for h in hogis]
    in_clause = "'" + "','".join(hogi_list) + "'"
    
    # 2. ELV_INFO$VF 에서 이 호기들의 EL_ABRAND, EL_ATYP 값 확인
    sql_elv = f"""
    SELECT E.MD$NUMBER AS HOGI, E.EL_ABRAND, HDEL_DEFAULT.COD(E.EL_ABRAND) AS COD_BRAND, E.EL_ATYP, HDEL_DEFAULT.COD(E.EL_ATYP) AS COD_ATYP
      FROM HDEL_DEFAULT.ELV_INFO$ID A, HDEL_DEFAULT.ELV_INFO$VF E
     WHERE A.ID$OUID = E.VF$IDENTITY AND E.vf$ouid = A.id$wip
       AND E.MD$NUMBER IN ({in_clause})
    """
    print("\nELV_INFO sample:", test_query(sql_elv))
