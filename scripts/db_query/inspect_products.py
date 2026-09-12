import urllib.request
import urllib.parse
import json

def execute_query(sql):
    url = 'https://vault-in.hdel.co.kr:8070/api/executeQuery?key=subae&sql=' + urllib.parse.quote(sql, safe='')
    req = urllib.request.urlopen(url)
    data = json.loads(req.read().decode('utf-8'))
    return data

# 1. PRODUCT$VF 총 건수 및 샘플 10개
sql_sample = """
SELECT MD$NUMBER, MD$STATUS, MD$CDATE, MD$MDATE
FROM PRODUCT$VF
WHERE ROWNUM <= 10
"""

# 2. PRODUCT$VF 의 MD$NUMBER 첫 글자 분포 (접두사 목록 및 건수)
sql_prefix = """
SELECT SUBSTR(MD$NUMBER, 1, 1) AS PREFIX, COUNT(*) AS CNT
FROM PRODUCT$VF
GROUP BY SUBSTR(MD$NUMBER, 1, 1)
ORDER BY CNT DESC
"""

print("=== 1. Sample 10 ===")
print(execute_query(sql_sample))

print("=== 2. Prefix Distribution ===")
print(execute_query(sql_prefix))
