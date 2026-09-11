import json
import ssl
from urllib.parse import urlencode
from urllib.request import Request, urlopen

API_URL = "https://vault-in.hdel.co.kr:8070/api/executeQuery"
API_KEY = "subae"

sql = """
SELECT H.PID,
       H.VERSION,
       H.HOUID,
       H.REG_DATE,
       H.USERID,
       (SELECT F.MD$DESC FROM FUSER$SF F WHERE F.MD$NUMBER = H.USERID) AS REG_USER_NAME,
       D.NO,
       NVL(D.ADDR, '-') AS ADDR
  FROM HDEL_DEFAULT.VARIANT_D D,
       HDEL_DEFAULT.VARIANT_H H
 WHERE H.HOUID = D.HOUID
   AND H.HOUID IN (1264930, 1304564)
 ORDER BY H.VERSION, TO_NUMBER(D.NO)
"""

def fetch_data(sql):
    query_string = urlencode({"key": API_KEY, "sql": sql})
    url = f"{API_URL}?{query_string}"
    req = Request(url, method="GET", headers={"Accept": "application/json"})
    context = ssl._create_unverified_context()
    with urlopen(req, timeout=120, context=context) as resp:
        raw = resp.read()
        try:
            text = raw.decode("utf-8")
        except:
            text = raw.decode("cp949", errors="replace")
        return json.loads(text)

data = fetch_data(sql)
print("Total rows:", len(data))
if data:
    print("Sample record:", data[0])
