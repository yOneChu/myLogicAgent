import json
import ssl
from urllib.parse import urlencode
from urllib.request import Request, urlopen

API_URL = "https://vault-in.hdel.co.kr:8070/api/executeQuery"
API_KEY = "subae"

def fetch_data(sql):
    query_string = urlencode({"key": API_KEY, "sql": sql})
    url = f"{API_URL}?{query_string}"
    req = Request(url, method="GET", headers={"Accept": "application/json"})
    context = ssl._create_unverified_context()
    with urlopen(req, timeout=60, context=context) as resp:
        raw = resp.read()
        try:
            text = raw.decode("utf-8")
        except:
            text = raw.decode("cp949", errors="replace")
        return json.loads(text)

v44_sql = "SELECT D.* FROM HDEL_DEFAULT.VARIANT_D D WHERE D.HOUID = 1292445 AND D.NO = '2'"
v45_sql = "SELECT D.* FROM HDEL_DEFAULT.VARIANT_D D WHERE D.HOUID = 1304784 AND D.NO = '2'"

r44 = fetch_data(v44_sql)
r45 = fetch_data(v45_sql)

print("=== NO = 2 v44 raw data ===")
print(json.dumps(r44, ensure_ascii=False, indent=2))

print("\n=== NO = 2 v45 raw data ===")
print(json.dumps(r45, ensure_ascii=False, indent=2))
