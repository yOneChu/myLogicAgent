import urllib.request
import json
import ssl
import urllib.parse
import sys
import io

if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

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
data = json.loads(req.read().decode('utf-8'))

print(f"Total matching rows in BOM_E321A: {len(data)}")
for r in data:
    rem = str(r.get('REMARKS', ''))
    val1 = str(r.get('VAL1', ''))
    val2 = str(r.get('VAL2', ''))
    print(f"NO {r.get('NO')}: ADDR='{r.get('ADDR')}' | SPEC1='{r.get('SPEC1')}', CON1='{r.get('CON1')}' | SPEC2='{r.get('SPEC2')}', CON2='{r.get('CON2')}' | KEY1='{r.get('KEY1')}', VAL1='{val1}' | REMARKS='{rem}'")
