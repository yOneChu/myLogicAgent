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

# B181B 자재 OUID (2249421386 -> hex 8613724a)
# 1. PE (PARTOFEBOM) 에서 해당 자재를 사용하고 있는 PRODUCTOUID 50개 샘플
sql_pe_sample = """
SELECT PE.PRODUCTOUID, A.MD$NUMBER AS HOGI, A.MD$STATUS, A.MD$MDATE, A.MD$CDATE
  FROM HDEL_DEFAULT.PARTOFEBOM PE
 INNER JOIN HDEL_DEFAULT.NORMALPART$VF NP ON PE.PARTOUID = NP.VF$OUID
 INNER JOIN HDEL_DEFAULT.PRODUCT$VF A ON PE.PRODUCTOUID = A.VF$OUID
 WHERE NP.BLOCKNO LIKE '%8613724a%'
   AND ROWNUM <= 50
"""
res = test_query(sql_pe_sample)
print(f"Sample 50 BOM rows with B181B parts (count: {len(res)}):")
for r in res[:10]:
    print(r)

# 2. 2026년 수정된 전체 PRODUCT$VF 의 MD$STATUS 통계
sql_2026_prods = """
SELECT A.MD$STATUS, COUNT(*) AS CNT
  FROM HDEL_DEFAULT.PRODUCT$VF A, HDEL_DEFAULT.PRODUCT$ID B
 WHERE A.VF$IDENTITY = B.ID$OUID AND A.VF$OUID = B.ID$WIP
   AND SUBSTR(A.MD$MDATE, 1, 4) = '2026'
 GROUP BY A.MD$STATUS
"""
print("2026 products by status:", test_query(sql_2026_prods))
