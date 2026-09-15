import json
import ssl
import os
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

v44_sql = "SELECT D.* FROM HDEL_DEFAULT.VARIANT_D D WHERE D.HOUID = 1292445 ORDER BY TO_NUMBER(D.NO)"
v45_sql = "SELECT D.* FROM HDEL_DEFAULT.VARIANT_D D WHERE D.HOUID = 1304784 ORDER BY TO_NUMBER(D.NO)"

v44_rows = fetch_data(v44_sql)
v45_rows = fetch_data(v45_sql)

print(f"v44 total rows: {len(v44_rows)}")
print(f"v45 total rows: {len(v45_rows)}")

def get_sig(r):
    if not r: return ""
    addr = str(r.get("ADDR") or "").strip()
    goto = str(r.get("GOTO") or "").strip()
    rem = str(r.get("REMARKS") or "").strip()
    specs = [f"{r.get(f'SPEC{i}')}:{r.get(f'CON{i}')}" for i in range(1, 31) if r.get(f'SPEC{i}') or r.get(f'CON{i}')]
    keys = [f"{r.get(f'KEY{i}')}:{r.get(f'VAL{i}')}" for i in range(1, 21) if r.get(f'KEY{i}') or r.get(f'VAL{i}')]
    return f"ADDR={addr}|GOTO={goto}|REMARKS={rem}|SPECS={','.join(specs)}|KEYS={','.join(keys)}"

v44_sigs = [get_sig(r) for r in v44_rows]
v45_sigs = [get_sig(r) for r in v45_rows]

print("\n--- Row-by-Row Compare for NO 1 to 10 ---")
for i in range(10):
    no44 = i + 1
    no45 = i + 1
    r44 = v44_rows[i] if i < len(v44_rows) else {}
    r45 = v45_rows[i] if i < len(v45_rows) else {}
    print(f"NO {no44:2d} v44: {get_sig(r44)}")
    print(f"      v45: {get_sig(r45)}")
    print()
