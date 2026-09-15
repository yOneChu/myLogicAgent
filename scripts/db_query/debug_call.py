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

v44_sql = "SELECT D.NO, D.KEY1, D.VAL1, D.REMARKS FROM HDEL_DEFAULT.VARIANT_D D WHERE D.HOUID = 1292445 ORDER BY TO_NUMBER(D.NO)"
v45_sql = "SELECT D.NO, D.KEY1, D.VAL1, D.REMARKS FROM HDEL_DEFAULT.VARIANT_D D WHERE D.HOUID = 1304784 ORDER BY TO_NUMBER(D.NO)"

v44 = fetch_data(v44_sql)
v45 = fetch_data(v45_sql)

print("--- Looking for CAL_FIRST_DATE ---")
print("v44:", [r for r in v44 if r.get("VAL1") == "CAL_FIRST_DATE"])
print("v45:", [r for r in v45 if r.get("VAL1") == "CAL_FIRST_DATE"])

print("\n--- Looking for CAL_NG550_CS ---")
print("v44:", [r for r in v44 if r.get("VAL1") == "CAL_NG550_CS"])
print("v45:", [r for r in v45 if r.get("VAL1") == "CAL_NG550_CS"])

print("\n--- Compare NO 1 to 5 in v44 vs v45 ---")
v44_by_no = {r["NO"]: r for r in v44}
v45_by_no = {r["NO"]: r for r in v45}

for i in range(1, 10):
    r44 = v44_by_no.get(i, {})
    r45 = v45_by_no.get(i, {})
    print(f"NO {i:2d} | v44: KEY1={r44.get('KEY1')}, VAL1={r44.get('VAL1')}, REMARKS={r44.get('REMARKS')}")
    print(f"      | v45: KEY1={r45.get('KEY1')}, VAL1={r45.get('VAL1')}, REMARKS={r45.get('REMARKS')}")
