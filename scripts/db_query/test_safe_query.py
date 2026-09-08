import json
import urllib.parse
import urllib.request
import ssl

API_URL = "https://vault-in.hdel.co.kr:8070/api/executeQuery"
API_KEY = "subae"

def run_query(sql, name):
    query_string = urllib.parse.urlencode({"key": API_KEY, "sql": sql})
    url = f"{API_URL}?{query_string}"
    req = urllib.request.Request(url, headers={"Accept": "application/json"})
    ctx = ssl._create_unverified_context()
    with urllib.request.urlopen(req, context=ctx, timeout=60) as resp:
        body = resp.read().decode("utf-8")
        data = json.loads(body)
        print(f"[{name}] Row count: {len(data)}")
        if len(data) > 0:
            print(f"[{name}] Sample 1st: {data[0]}")

q_tonumber = """
WITH ouid AS (
    SELECT A.vf$ouid AS VFOID
      FROM HDEL_DEFAULT.product$vf A, HDEL_DEFAULT.product$id B
     WHERE A.vf$identity = B.id$ouid
       AND A.vf$ouid     = B.id$wip
       AND A.MD$NUMBER NOT LIKE 'TEST%'
       AND A.MD$NUMBER NOT LIKE 'Q%'
       AND A.MD$NUMBER LIKE 'V%'
       AND SUBSTR(A.MD$CDATE, 1, 4) = '2026'
)
SELECT NP.MD$NUMBER AS PARTNO,
       NP.BLOCKNO AS RAW_BLOCKNO,
       (SELECT B.MD$NUMBER FROM HDEL_DEFAULT.BLOCKNO$SF B
         WHERE B.SF$OUID = (CASE WHEN NP.BLOCKNO IS NOT NULL AND INSTR(NP.BLOCKNO, '@') > 0
                                 THEN TO_NUMBER(UPPER(SUBSTR(NP.BLOCKNO, INSTR(NP.BLOCKNO, '@') + 1)), 'XXXXXXXX')
                                 ELSE NULL END)) AS BLOCKNO
  FROM HDEL_DEFAULT.PARTOFEBOM PE
 INNER JOIN HDEL_DEFAULT.NORMALPART$VF NP ON PE.PARTOUID = NP.VF$OUID
 WHERE PE.PRODUCTOUID IN (SELECT VFOID FROM ouid)
   AND NP.BLOCKNO IS NOT NULL
   AND ROWNUM <= 10
"""
run_query(q_tonumber, "TO_NUMBER BlockNo Query")
