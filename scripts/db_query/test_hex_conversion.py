# -*- coding: utf-8 -*-
import json
import urllib.parse
import urllib.request
import ssl

ctx = ssl._create_unverified_context()

def run_sql(sql):
    url = "https://vault-in.hdel.co.kr:8070/api/executeQuery?" + urllib.parse.urlencode({
        "key": "subae",
        "sql": sql
    })
    req = urllib.request.Request(url, headers={"Accept": "application/json"})
    try:
        with urllib.request.urlopen(req, context=ctx, timeout=60) as resp:
            return json.loads(resp.read().decode('utf-8', errors='ignore'))
    except Exception as e:
        return f"Error: {e}"

# Test 1: TO_NUMBER hex 변환
print("1. TO_NUMBER hex 변환 테스트:")
q1 = "SELECT TO_NUMBER('8613735b', 'XXXXXXXX') AS DEC_NUM FROM DUAL"
print(run_sql(q1))

# Test 2: NORMALPART$VF 의 BLOCKNO를 TO_NUMBER로 연동하여 BLOCKNO$SF조회
print("\n2. NORMALPART$VF와 BLOCKNO$SF 매칭 테스트 5건:")
q2 = """
SELECT NP.MD$NUMBER, NP.BLOCKNO, 
       (SELECT B.MD$NUMBER FROM HDEL_DEFAULT.BLOCKNO$SF B 
         WHERE B.SF$OUID = TO_NUMBER(UPPER(SUBSTR(NP.BLOCKNO, 12)), 'XXXXXXXX')) AS BLOCK_NAME
  FROM HDEL_DEFAULT.NORMALPART$VF NP
 WHERE NP.BLOCKNO IS NOT NULL AND ROWNUM <= 5
"""
print(run_sql(q2))

# Test 3: A101A 계열 블럭 수배 2026년 데이터 조회
print("\n3. A101A 계열 2026년 데이터 건수:")
q3 = """
WITH ouid AS (
    SELECT A.vf$ouid AS VFOID
      FROM HDEL_DEFAULT.product$vf A, HDEL_DEFAULT.product$id B
     WHERE A.vf$identity = B.id$ouid
       AND A.vf$ouid     = B.id$wip
       AND A.MD$NUMBER NOT LIKE 'TEST%'
       AND A.MD$NUMBER NOT LIKE 'Q%'
       AND SUBSTR(A.MD$MDATE, 1, 4) = '2026'
)
SELECT COUNT(*) AS CNT, COUNT(DISTINCT PE.PRODUCTOUID) AS PROD_CNT
  FROM HDEL_DEFAULT.PARTOFEBOM PE
 INNER JOIN HDEL_DEFAULT.NORMALPART$VF NP ON PE.PARTOUID = NP.VF$OUID
 WHERE PE.PRODUCTOUID IN (SELECT VFOID FROM ouid)
   AND (SELECT B.MD$NUMBER FROM HDEL_DEFAULT.BLOCKNO$SF B
         WHERE B.SF$OUID = TO_NUMBER(UPPER(SUBSTR(NP.BLOCKNO, 12)), 'XXXXXXXX')) LIKE 'A101A%'
"""
print(run_sql(q3))
