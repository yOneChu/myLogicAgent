import urllib.request
import urllib.parse
import json

def execute_query(sql):
    url = 'https://vault-in.hdel.co.kr:8070/api/executeQuery?key=subae&sql=' + urllib.parse.quote(sql, safe='')
    req = urllib.request.urlopen(url)
    data = json.loads(req.read().decode('utf-8'))
    return data

# 1. 전체 PRODUCT$VF 데이터 기준 (V로 시작하는 제품)
sql1 = """
SELECT 
    COUNT(*) AS TOTAL_ROWS,
    COUNT(DISTINCT MD$NUMBER) AS DISTINCT_HOGI_COUNT
FROM PRODUCT$VF
WHERE MD$NUMBER LIKE 'V%'
"""

# 2. 유효 버전(WIP) 기준 V로 시작하는 제품 건수 (전체 및 TEST/Q 제외)
sql2 = """
SELECT 
    COUNT(DISTINCT A.MD$NUMBER) AS WIP_DISTINCT_HOGI,
    COUNT(CASE WHEN A.MD$NUMBER NOT LIKE 'TEST%' AND A.MD$NUMBER NOT LIKE 'Q%' THEN 1 END) AS WIP_NON_TEST_Q
FROM PRODUCT$VF A, PRODUCT$ID B
WHERE A.vf$identity = B.id$ouid
  AND A.vf$ouid     = B.id$wip
  AND A.MD$NUMBER LIKE 'V%'
"""

# 3. 유효 버전 기준 상태별 건수
sql3 = """
SELECT 
    A.MD$STATUS,
    COUNT(DISTINCT A.MD$NUMBER) AS HOGI_CNT
FROM PRODUCT$VF A, PRODUCT$ID B
WHERE A.vf$identity = B.id$ouid
  AND A.vf$ouid     = B.id$wip
  AND A.MD$NUMBER LIKE 'V%'
GROUP BY A.MD$STATUS
ORDER BY HOGI_CNT DESC
"""

# 4. 연도별(제품 수정일 기준) 건수
sql4 = """
SELECT 
    SUBSTR(A.MD$MDATE, 1, 4) AS MOD_YEAR,
    COUNT(DISTINCT A.MD$NUMBER) AS HOGI_CNT
FROM PRODUCT$VF A, PRODUCT$ID B
WHERE A.vf$identity = B.id$ouid
  AND A.vf$ouid     = B.id$wip
  AND A.MD$NUMBER LIKE 'V%'
GROUP BY SUBSTR(A.MD$MDATE, 1, 4)
ORDER BY MOD_YEAR DESC
"""

print("=== 1. 전체 PRODUCT$VF 기준 ===")
res1 = execute_query(sql1)
print(json.dumps(res1, ensure_ascii=False, indent=2))

print("=== 2. 유효 버전(WIP) 기준 ===")
res2 = execute_query(sql2)
print(json.dumps(res2, ensure_ascii=False, indent=2))

print("=== 3. 상태별 건수 (WIP 기준) ===")
res3 = execute_query(sql3)
print(json.dumps(res3, ensure_ascii=False, indent=2))

print("=== 4. 제품 수정연도별 건수 (WIP 기준) ===")
res4 = execute_query(sql4)
print(json.dumps(res4, ensure_ascii=False, indent=2))
