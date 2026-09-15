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

def get_row_summary_dict(r):
    if not r: return {}
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
    return {
        "addr": addr,
        "goto": goto,
        "remarks": remarks,
        "specs": specs,
        "keys": keys,
        "signature": f"ADDR={addr}|GOTO={goto}|REMARKS={remarks}|SPECS={','.join(specs)}|KEYS={','.join(keys)}"
    }

v44_data = {int(r["NO"]): get_row_summary_dict(r) for r in v44_rows}
v45_data = {int(r["NO"]): get_row_summary_dict(r) for r in v45_rows}

v44_sigs = {no: d["signature"] for no, d in v44_data.items()}
v45_sigs = {no: d["signature"] for no, d in v45_data.items()}

# 1. Unchanged rows (Exact NO & Signature match)
unchanged = []
for no in range(1, 151):
    if v44_sigs.get(no) and v45_sigs.get(no) and v44_sigs[no] == v45_sigs[no]:
        unchanged.append(no)

# 2. Purely Added in v45 (Signature not anywhere in v44)
v44_all_sigs = set(v44_sigs.values())
pure_added = []
for no, sig in v45_sigs.items():
    if sig not in v44_all_sigs:
        pure_added.append((no, v45_data[no]))

# 3. Purely Deleted in v45 (Signature not anywhere in v45)
v45_all_sigs = set(v45_sigs.values())
pure_deleted = []
for no, sig in v44_sigs.items():
    if sig not in v45_all_sigs:
        pure_deleted.append((no, v44_data[no]))

# 4. Line shifted (Exact Signature matches, but different NO)
shifted = []
for no44, sig in v44_sigs.items():
    if sig in v45_all_sigs:
        no45_list = [no for no, s in v45_sigs.items() if s == sig]
        if no44 not in no45_list:
            shifted.append({"v44_no": no44, "v45_nos": no45_list, "signature": sig})

print(f"Unchanged rows count: {len(unchanged)} (NOs: {unchanged[:10]} ... {unchanged[-5:]})")
print(f"Purely Added count: {len(pure_added)}")
for no, d in pure_added:
    print(f"  v45 NO {no}: REMARKS='{d['remarks']}', SPECS={d['specs']}, KEYS={d['keys']}")

print(f"\nPurely Deleted count: {len(pure_deleted)}")
for no, d in pure_deleted:
    print(f"  v44 NO {no}: REMARKS='{d['remarks']}', SPECS={d['specs']}, KEYS={d['keys']}")

print(f"\nLine Shifted count: {len(shifted)}")
for s in shifted[:10]:
    print(f"  v44 NO {s['v44_no']} ==> v45 NO {s['v45_nos']}")
