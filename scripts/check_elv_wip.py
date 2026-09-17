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

print("--- WIP 조건 적용 ELV_INFO 샘플 10개 ---")
sql = """
SELECT E.MD$NUMBER, E.EL_ABRAND, E.EL_ATYP
  FROM HDEL_DEFAULT.ELV_INFO$VF E, HDEL_DEFAULT.ELV_INFO$ID A
 WHERE A.ID$OUID = E.VF$IDENTITY AND E.vf$ouid = A.id$wip
   AND ROWNUM <= 10
"""
res = query(sql)
print(res)

