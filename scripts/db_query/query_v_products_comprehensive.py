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

# 1. 전체 PRODUCT$VF 기준 (모든 버전 포함)
sql_all = """
SELECT 
    COUNT(*) AS TOTAL_ROW_COUNT,
    COUNT(DISTINCT MD$NUMBER) AS DISTINCT_PRODUCT_COUNT
FROM HDEL_DEFAULT.PRODUCT$VF
WHERE MD$NUMBER LIKE 'V%'
"""

# 2. 유효버전(WIP) 기준 V 제품 수
sql_wip = """
SELECT 
    COUNT(DISTINCT A.MD$NUMBER) AS WIP_DISTINCT_PRODUCT,
    COUNT(CASE WHEN A.MD$NUMBER NOT LIKE 'TEST%' AND A.MD$NUMBER NOT LIKE 'Q%' THEN 1 END) AS WIP_NORMAL_PRODUCT
FROM HDEL_DEFAULT.PRODUCT$VF A, HDEL_DEFAULT.PRODUCT$ID B
WHERE A.vf$identity = B.id$ouid
  AND A.vf$ouid     = B.id$wip
  AND A.MD$NUMBER LIKE 'V%'
"""

# 3. 유효버전 기준 상태(MD$STATUS)별 제품 수
sql_status = """
SELECT 
    A.MD$STATUS,
    COUNT(DISTINCT A.MD$NUMBER) AS HOGI_CNT
FROM HDEL_DEFAULT.PRODUCT$VF A, HDEL_DEFAULT.PRODUCT$ID B
WHERE A.vf$identity = B.id$ouid
  AND A.vf$ouid     = B.id$wip
  AND A.MD$NUMBER LIKE 'V%'
GROUP BY A.MD$STATUS
ORDER BY HOGI_CNT DESC
"""

# 4. 유효버전 기준 등록연도(MD$CDATE)별 분포
sql_cdate_year = """
SELECT 
    SUBSTR(A.MD$CDATE, 1, 4) AS CRE_YEAR,
    COUNT(DISTINCT A.MD$NUMBER) AS HOGI_CNT
FROM HDEL_DEFAULT.PRODUCT$VF A, HDEL_DEFAULT.PRODUCT$ID B
WHERE A.vf$identity = B.id$ouid
  AND A.vf$ouid     = B.id$wip
  AND A.MD$NUMBER LIKE 'V%'
GROUP BY SUBSTR(A.MD$CDATE, 1, 4)
ORDER BY CRE_YEAR DESC
"""

# 5. 유효버전 기준 수정연도(MD$MDATE)별 분포
sql_mdate_year = """
SELECT 
    SUBSTR(A.MD$MDATE, 1, 4) AS MOD_YEAR,
    COUNT(DISTINCT A.MD$NUMBER) AS HOGI_CNT
FROM HDEL_DEFAULT.PRODUCT$VF A, HDEL_DEFAULT.PRODUCT$ID B
WHERE A.vf$identity = B.id$ouid
  AND A.vf$ouid     = B.id$wip
  AND A.MD$NUMBER LIKE 'V%'
GROUP BY SUBSTR(A.MD$MDATE, 1, 4)
ORDER BY MOD_YEAR DESC
"""

# 6. 샘플 제품번호 10개
sql_samples = """
SELECT A.MD$NUMBER, A.MD$STATUS, A.MD$CDATE, A.MD$MDATE
FROM HDEL_DEFAULT.PRODUCT$VF A, HDEL_DEFAULT.PRODUCT$ID B
WHERE A.vf$identity = B.id$ouid
  AND A.vf$ouid     = B.id$wip
  AND A.MD$NUMBER LIKE 'V%'
  AND ROWNUM <= 10
ORDER BY A.MD$CDATE DESC
"""

print("=== 1. 전체 PRODUCT$VF 기준 (모든 버전) ===")
print(run_sql(sql_all))

print("\n=== 2. 유효버전(WIP) 기준 ===")
print(run_sql(sql_wip))

print("\n=== 3. 상태별 분포 (WIP 기준) ===")
print(run_sql(sql_status))

print("\n=== 4. 등록연도별 분포 (WIP 기준) ===")
print(run_sql(sql_cdate_year))

print("\n=== 5. 수정연도별 분포 (WIP 기준) ===")
print(run_sql(sql_mdate_year))

print("\n=== 6. 샘플 제품번호 10개 ===")
print(run_sql(sql_samples))
