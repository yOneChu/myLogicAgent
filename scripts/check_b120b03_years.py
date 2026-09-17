import urllib.request
import urllib.parse
import ssl
import json

def query(sql):
    url = 'https://vault-in.hdel.co.kr:8070/api/executeQuery'
    params = {'key': 'subae', 'sql': sql}
    full_url = url + '?' + urllib.parse.urlencode(params)
    ctx = ssl._create_unverified_context()
    req = urllib.request.Request(full_url, headers={'Accept': 'application/json', 'User-Agent': 'Mozilla/5.0'})
    with urllib.request.urlopen(req, context=ctx, timeout=120) as resp:
        return json.loads(resp.read().decode('utf-8', errors='replace'))

print("--- B120B03 블록 적용 제품 연도별 집계 ---")
sql = """
SELECT SUBSTR(A.MD$MDATE, 1, 4) AS MOD_YEAR,
       COUNT(DISTINCT PE.PRODUCTOUID) AS PROD_CNT,
       COUNT(*) AS BOM_CNT
  FROM HDEL_DEFAULT.PARTOFEBOM PE
 INNER JOIN HDEL_DEFAULT.NORMALPART$VF NP ON PE.PARTOUID = NP.VF$OUID
 INNER JOIN HDEL_DEFAULT.PRODUCT$VF A ON PE.PRODUCTOUID = A.VF$OUID
 INNER JOIN HDEL_DEFAULT.PRODUCT$ID B ON A.VF$IDENTITY = B.ID$OUID AND A.VF$OUID = B.ID$WIP
 WHERE A.MD$NUMBER NOT LIKE 'TEST%'
   AND A.MD$NUMBER NOT LIKE 'Q%'
   AND TO_NUMBER(UPPER(SUBSTR(NP.BLOCKNO, 12)), 'XXXXXXXX') = (SELECT SF$OUID FROM HDEL_DEFAULT.BLOCKNO$SF WHERE MD$NUMBER = 'B120B03')
 GROUP BY SUBSTR(A.MD$MDATE, 1, 4)
 ORDER BY MOD_YEAR DESC
"""
res = query(sql)
print("연도별 분포:", res)

