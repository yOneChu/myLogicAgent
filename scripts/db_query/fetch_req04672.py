import urllib.request
import json
import ssl
import urllib.parse

ctx = ssl._create_unverified_context()
sql = """
SELECT A.MD$NUMBER AS REQNO,
       A.MD$STATUS,
       A.MD$DESC,
       A.MD$USER,
       (SELECT U.MD$DESC FROM FUSER$SF U WHERE U.MD$NUMBER = A.MD$USER) AS MUSER,
       A.MANAGER,
       A.HOGI,
       A.REQUESTDETAIL,
       A.ANSWERDETAIL,
       A.MD$CDATE
  FROM HDEL_DEFAULT.NEWPLMDESIGNREQUEST$VF A
 WHERE A.MD$NUMBER = '04672' OR A.MD$NUMBER = '4672' OR A.MD$NUMBER LIKE '%4672%'
"""

url = 'https://vault-in.hdel.co.kr:8070/api/executeQuery?' + urllib.parse.urlencode({'key':'subae', 'sql': sql.strip()})
req = urllib.request.urlopen(url, context=ctx)
res = json.loads(req.read().decode('utf-8'))

out_path = r'd:\Antigravity_workspace\myLogicAgent\output_req04672.json'
with open(out_path, 'w', encoding='utf-8') as f:
    json.dump(res, f, ensure_ascii=False, indent=2)

print("DATA:", json.dumps(res, ensure_ascii=False))
