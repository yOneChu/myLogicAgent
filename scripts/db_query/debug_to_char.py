import json
import ssl
from urllib.parse import urlencode
from urllib.request import Request, urlopen

API_URL = "https://vault-in.hdel.co.kr:8070/api/executeQuery"
API_KEY = "subae"

sql = """
SELECT H.PID,
       H.VERSION,
       H.HOUID AS H_HOUID,
       D.HOUID AS D_HOUID,
       D.NO,
       NVL(D.ADDR, '-') AS ADDR
  FROM HDEL_DEFAULT.VARIANT_D D,
       HDEL_DEFAULT.VARIANT_H H
 WHERE TO_CHAR(H.HOUID) = TO_CHAR(D.HOUID)
   AND TO_CHAR(H.HOUID) IN ('1264930', '1304564')
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
print("Total rows with TO_CHAR join:", len(data))
if data:
    print("Sample record:", data[0])
