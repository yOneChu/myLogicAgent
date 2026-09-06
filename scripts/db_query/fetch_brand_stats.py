# -*- coding: utf-8 -*-
import json
import urllib.parse
import urllib.request
import ssl
import pandas as pd

ctx = ssl._create_unverified_context()

def run_sql(sql):
    url = "https://vault-in.hdel.co.kr:8070/api/executeQuery?" + urllib.parse.urlencode({
        "key": "subae",
        "sql": sql
    })
    req = urllib.request.Request(url, headers={"Accept": "application/json"})
    with urllib.request.urlopen(req, context=ctx, timeout=120) as resp:
        return json.loads(resp.read().decode('utf-8', errors='ignore'))

# 1. 브랜드별 호기 수 및 수배 건수 집계
sql_brand_summary = """
WITH ouid AS (
    SELECT A.vf$ouid AS VFOID
      FROM HDEL_DEFAULT.product$vf A, HDEL_DEFAULT.product$id B
     WHERE A.vf$identity = B.id$ouid
       AND A.vf$ouid     = B.id$wip
       AND A.MD$NUMBER NOT LIKE 'TEST%'
       AND A.MD$NUMBER NOT LIKE 'Q%'
       AND SUBSTR(A.MD$MDATE, 1, 4) = '2026'
)
SELECT 
    NVL(HDEL_DEFAULT.COD(E.EL_ABRAND), '기타/미정') AS BRAND,
    COUNT(DISTINCT PE.PRODUCTOUID) AS PROD_CNT,
    COUNT(*) AS TOTAL_BOM_CNT
  FROM HDEL_DEFAULT.PARTOFEBOM PE
 INNER JOIN HDEL_DEFAULT.NORMALPART$VF NP ON PE.PARTOUID = NP.VF$OUID
  LEFT OUTER JOIN HDEL_DEFAULT.ELV_INFO$VF E ON E.MD$NUMBER = (SELECT F.MD$NUMBER FROM HDEL_DEFAULT.PRODUCT$VF F WHERE F.VF$OUID = PE.PRODUCTOUID)
  LEFT OUTER JOIN HDEL_DEFAULT.ELV_INFO$ID EI ON EI.ID$OUID = E.VF$IDENTITY AND E.vf$ouid = EI.id$wip
 WHERE PE.PRODUCTOUID IN (SELECT VFOID FROM ouid)
   AND (SELECT B.MD$NUMBER FROM HDEL_DEFAULT.BLOCKNO$SF B
         WHERE B.SF$OUID = TO_NUMBER(UPPER(SUBSTR(NP.BLOCKNO, 12)), 'XXXXXXXX')) LIKE 'A101A%'
 GROUP BY NVL(HDEL_DEFAULT.COD(E.EL_ABRAND), '기타/미정')
 ORDER BY PROD_CNT DESC
"""

print("=== 1. 브랜드별 집계 요약 ===")
brands = run_sql(sql_brand_summary)
print(pd.DataFrame(brands))
