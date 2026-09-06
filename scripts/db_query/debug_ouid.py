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

# 1. 2026년 OUID 수
print("1. 2026년 ouid 수:")
q1 = """
SELECT COUNT(A.vf$ouid) AS CNT
  FROM HDEL_DEFAULT.product$vf A, HDEL_DEFAULT.product$id B
 WHERE A.vf$identity = B.id$ouid
   AND A.vf$ouid     = B.id$wip
   AND A.MD$NUMBER NOT LIKE 'TEST%'
   AND A.MD$NUMBER NOT LIKE 'Q%'
   AND SUBSTR(A.MD$MDATE, 1, 4) = '2026'
"""
print(run_sql(q1))

# 2. PARTOFEBOM의 PRODUCTOUID와 product$vf matching 수
print("2. PARTOFEBOM과 product$vf OUID 매칭 수:")
q2 = """
WITH ouid AS (
    SELECT A.vf$ouid AS VFOID
      FROM HDEL_DEFAULT.product$vf A, HDEL_DEFAULT.product$id B
     WHERE A.vf$identity = B.id$ouid
       AND A.vf$ouid     = B.id$wip
       AND A.MD$NUMBER NOT LIKE 'TEST%'
       AND A.MD$NUMBER NOT LIKE 'Q%'
       AND SUBSTR(A.MD$MDATE, 1, 4) = '2026'
)
SELECT COUNT(*) AS CNT FROM HDEL_DEFAULT.PARTOFEBOM PE
 WHERE PE.PRODUCTOUID IN (SELECT VFOID FROM ouid)
   AND ROWNUM <= 10
"""
print(run_sql(q2))

# 3. BLOCKNO$SF와 NORMALPART$VF 의 연결 방식 검증
print("3. NORMALPART$VF의 BLOCKNO 형태 10건 샘플:")
q3 = "SELECT MD$NUMBER, BLOCKNO, HEXTODEC(UPPER(SUBSTR(BLOCKNO, 12))) AS OUID_NUM FROM HDEL_DEFAULT.NORMALPART$VF WHERE BLOCKNO IS NOT NULL AND ROWNUM <= 5"
print(run_sql(q3))

# 4. A101A 자재가 NORMALPART$VF에 수배된 건
print("4. BLOCKNO가 A101A인 NORMALPART$VF 수:")
q4 = """
SELECT COUNT(*) AS CNT
  FROM HDEL_DEFAULT.NORMALPART$VF NP
 WHERE (SELECT MD$NUMBER FROM HDEL_DEFAULT.BLOCKNO$SF
         WHERE SF$OUID = DECODE(NP.BLOCKNO, NULL, NULL, HEXTODEC(UPPER(SUBSTR(NP.BLOCKNO, 12))))) LIKE 'A101A%'
"""
print(run_sql(q4))

