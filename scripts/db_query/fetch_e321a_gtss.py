import urllib.request
import json
import ssl
import urllib.parse

ctx = ssl._create_unverified_context()
sql = """
SELECT D.NO, D.ADDR, D.SPEC1, D.CON1, D.SPEC2, D.CON2, D.SPEC3, D.CON3, D.KEY1, D.VAL1, D.KEY2, D.VAL2, D.GOTO, D.REMARKS
  FROM HDEL_DEFAULT.VARIANT_D D, HDEL_DEFAULT.VARIANT_H H
 WHERE H.PID = 'BOM_E321A'
   AND H.HOUID = D.HOUID
   AND H.VERSION = (SELECT MAX(VERSION) FROM HDEL_DEFAULT.VARIANT_H WHERE PID = 'BOM_E321A')
   AND (D.REMARKS LIKE '%4672%' OR D.REMARKS LIKE '%GTSS%' OR D.VAL1 LIKE '%GTSS%' OR D.VAL2 LIKE '%GTSS%')
 ORDER BY D.NO
"""

url = 'https://vault-in.hdel.co.kr:8070/api/executeQuery?' + urllib.parse.urlencode({'key':'subae', 'sql': sql.strip()})
req = urllib.request.urlopen(url, context=ctx)
res = json.loads(req.read().decode('utf-8'))

out_path = r'd:\Antigravity_workspace\myLogicAgent\output_e321a_gtss.json'
with open(out_path, 'w', encoding='utf-8') as f:
    json.dump(res, f, ensure_ascii=False, indent=2)

print(f"Saved {len(res)} matching rows to {out_path}")
