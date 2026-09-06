# -*- coding: utf-8 -*-
"""
A101A 블럭 및 2026년 데이터 존재 여부 확인 테스트 스크립트
"""

import json
import urllib.parse
import urllib.request
import ssl

# SSL 인증서 검증 비활성화
ctx = ssl._create_unverified_context()

def run_sql(sql):
    """
    SQL을 API에 전송하여 결과 JSON을 반환하는 함수
    """
    url = "https://vault-in.hdel.co.kr:8070/api/executeQuery?" + urllib.parse.urlencode({
        "key": "subae",
        "sql": sql
    })
    req = urllib.request.Request(url, headers={"Accept": "application/json"})
    with urllib.request.urlopen(req, context=ctx, timeout=60) as resp:
        return json.loads(resp.read().decode('utf-8', errors='ignore'))

# 1. 2026년 product$vf 건수 확인
print("1. 2026년 product$vf 건수:")
q1 = "SELECT COUNT(*) AS CNT FROM product$vf WHERE SUBSTR(MD$MDATE, 0, 4) = '2026'"
print(run_sql(q1))

# 2. BLOCKNO$SF에서 A101A 검색
print("\n2. BLOCKNO$SF에서 A101A 번호 조회:")
q2 = "SELECT SF$OUID, MD$NUMBER FROM BLOCKNO$SF WHERE MD$NUMBER LIKE '%A101A%'"
print(run_sql(q2))

# 3. 2026년 호기 연도 조건 없이 A101A 수배 데이터 검색
print("\n3. A101A 블럭 자재 수배 건수 (연도제한 없이 10건):")
q3 = """
SELECT PE.PRODUCTOUID, NP.MD$NUMBER, NP.MD$DESC, NP.BLOCKNO 
  FROM PARTOFEBOM PE 
 INNER JOIN NORMALPART$VF NP ON PE.PARTOUID = NP.VF$OUID 
 WHERE (SELECT MD$NUMBER FROM BLOCKNO$SF WHERE SF$OUID = DECODE(NP.BLOCKNO, NULL, NULL, HEXTODEC(UPPER(SUBSTR(NP.BLOCKNO, 12))))) = 'A101A'
   AND ROWNUM <= 5
"""
print(run_sql(q3))

# 4. A101A 자재가 수배된 product의 연도 분포 확인
print("\n4. A101A 수배 제품의 MD$MDATE 연도 분포:")
q4 = """
SELECT SUBSTR(A.MD$MDATE, 1, 4) AS YYYY, COUNT(*) AS CNT
  FROM PARTOFEBOM PE
 INNER JOIN NORMALPART$VF NP ON PE.PARTOUID = NP.VF$OUID
 INNER JOIN PRODUCT$VF A ON PE.PRODUCTOUID = A.VF$OUID
 WHERE (SELECT MD$NUMBER FROM BLOCKNO$SF WHERE SF$OUID = DECODE(NP.BLOCKNO, NULL, NULL, HEXTODEC(UPPER(SUBSTR(NP.BLOCKNO, 12))))) = 'A101A'
 GROUP BY SUBSTR(A.MD$MDATE, 1, 4)
 ORDER BY YYYY DESC
"""
print(run_sql(q4))
