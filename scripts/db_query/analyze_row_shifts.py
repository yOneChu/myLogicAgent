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

v44_houid = 1292445
v45_houid = 1304784

v44_sql = f"SELECT '44' AS VERSION, D.* FROM HDEL_DEFAULT.VARIANT_D D WHERE D.HOUID = {v44_houid} ORDER BY TO_NUMBER(D.NO)"
v45_sql = f"SELECT '45' AS VERSION, D.* FROM HDEL_DEFAULT.VARIANT_D D WHERE D.HOUID = {v45_houid} ORDER BY TO_NUMBER(D.NO)"

v44_rows = fetch_data(v44_sql)
v45_rows = fetch_data(v45_sql)

def make_signature(r):
    if not r: return ""
    addr = str(r.get("ADDR") or "").strip()
    goto = str(r.get("GOTO") or "").strip()
    remarks = str(r.get("REMARKS") or "").strip()
    specs = []
    for i in range(1, 31):
        s = str(r.get(f"SPEC{i}") or "").strip()
        c = str(r.get(f"CON{i}") or "").strip()
        if s or c:
            specs.append(f"{s}:{c}")
    keys = []
    for i in range(1, 21):
        k = str(r.get(f"KEY{i}") or "").strip()
        v = str(r.get(f"VAL{i}") or "").strip()
        if k or v:
            keys.append(f"{k}:{v}")
    return f"ADDR={addr}|GOTO={goto}|REMARKS={remarks}|SPECS={','.join(specs)}|KEYS={','.join(keys)}"

v44_sig_map = {int(r["NO"]): make_signature(r) for r in v44_rows}
v45_sig_map = {int(r["NO"]): make_signature(r) for r in v45_rows}

# Check content shifts
v44_sigs = [(int(r["NO"]), make_signature(r)) for r in v44_rows]
v45_sigs = [(int(r["NO"]), make_signature(r)) for r in v45_rows]

v44_content_to_nos = {}
for no, sig in v44_sigs:
    v44_content_to_nos.setdefault(sig, []).append(no)

v45_content_to_nos = {}
for no, sig in v45_sigs:
    v45_content_to_nos.setdefault(sig, []).append(no)

moved_rows = []
pure_added_contents = []
pure_deleted_contents = []

for sig, v45_nos in v45_content_to_nos.items():
    if sig in v44_content_to_nos:
        v44_nos = v44_content_to_nos[sig]
        if v44_nos != v45_nos:
            moved_rows.append({
                "v44_nos": v44_nos,
                "v45_nos": v45_nos,
                "signature": sig
            })
    else:
        pure_added_contents.append({"v45_nos": v45_nos, "signature": sig})

for sig, v44_nos in v44_content_to_nos.items():
    if sig not in v45_content_to_nos:
        pure_deleted_contents.append({"v44_nos": v44_nos, "signature": sig})

print(f"Total moved/shifted content signatures: {len(moved_rows)}")
print(f"Purely added content signatures (not present in v44): {len(pure_added_contents)}")
print(f"Purely deleted content signatures (not present in v45): {len(pure_deleted_contents)}")

print("\n--- Moved Rows Details (Line Shifted) ---")
for m in moved_rows:
    print(f"v44 NO {m['v44_nos']} ==> v45 NO {m['v45_nos']}")
    print(f"  Content: {m['signature'][:120]}...")

print("\n--- Purely Added Contents ---")
for a in pure_added_contents:
    print(f"v45 NO {a['v45_nos']}: {a['signature']}")

print("\n--- Purely Deleted Contents ---")
for d in pure_deleted_contents:
    print(f"v44 NO {d['v44_nos']}: {d['signature']}")
