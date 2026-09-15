import json
import ssl
import csv
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

v44_houid = 1292445
v45_houid = 1304784

print("Fetching v44 detail (HOUID: 1292445)...")
v44_sql = f"SELECT '44' AS VERSION, D.* FROM HDEL_DEFAULT.VARIANT_D D WHERE D.HOUID = {v44_houid} ORDER BY TO_NUMBER(D.NO)"
v44_rows = fetch_data(v44_sql)
print(f"v44 fetched: {len(v44_rows)} rows")

print("Fetching v45 detail (HOUID: 1304784)...")
v45_sql = f"SELECT '45' AS VERSION, D.* FROM HDEL_DEFAULT.VARIANT_D D WHERE D.HOUID = {v45_houid} ORDER BY TO_NUMBER(D.NO)"
v45_rows = fetch_data(v45_sql)
print(f"v45 fetched: {len(v45_rows)} rows")

os.makedirs("output_csv", exist_ok=True)
os.makedirs("output_excel", exist_ok=True)

# Save raw output to CSV
data = v44_rows + v45_rows
if data:
    headers = list(data[0].keys())
    with open("output_csv/EL_PA103A03_v44_v45_raw.csv", "w", newline="", encoding="utf-8-sig") as f:
        writer = csv.DictWriter(f, fieldnames=headers)
        writer.writeheader()
        writer.writerows(data)

# Index by NO
v44_by_no = {int(r["NO"]): r for r in v44_rows}
v45_by_no = {int(r["NO"]): r for r in v45_rows}

all_nos = sorted(list(set(v44_by_no.keys()) | set(v45_by_no.keys())))

differences = []
ignore_fields = {"VERSION", "REG_DATE", "USERID", "REG_USER_NAME", "HOUID", "PID"}

def get_active_pairs(r, prefix_a, prefix_b, count):
    pairs = []
    for i in range(1, count + 1):
        a = r.get(f"{prefix_a}{i}")
        b = r.get(f"{prefix_b}{i}")
        a_str = str(a).strip() if a is not None else ""
        b_str = str(b).strip() if b is not None else ""
        if a_str != "" or b_str != "":
            pairs.append(f"{a_str}:{b_str}")
    return pairs

for no in all_nos:
    r44 = v44_by_no.get(no)
    r45 = v45_by_no.get(no)
    
    if r44 is None:
        specs = get_active_pairs(r45, "SPEC", "CON", 30)
        keys = get_active_pairs(r45, "KEY", "VAL", 20)
        differences.append({
            "NO": no,
            "TYPE": "ADDED_IN_V45",
            "ADDR": r45.get("ADDR"),
            "GOTO": r45.get("GOTO"),
            "REMARKS": r45.get("REMARKS"),
            "SPECS": specs,
            "KEYS": keys,
            "v45_raw": r45
        })
    elif r45 is None:
        specs = get_active_pairs(r44, "SPEC", "CON", 30)
        keys = get_active_pairs(r44, "KEY", "VAL", 20)
        differences.append({
            "NO": no,
            "TYPE": "DELETED_IN_V45",
            "ADDR": r44.get("ADDR"),
            "GOTO": r44.get("GOTO"),
            "REMARKS": r44.get("REMARKS"),
            "SPECS": specs,
            "KEYS": keys,
            "v44_raw": r44
        })
    else:
        field_diffs = {}
        for k in r44.keys():
            if k in ignore_fields:
                continue
            val44 = str(r44.get(k) if r44.get(k) is not None else "").strip()
            val45 = str(r45.get(k) if r45.get(k) is not None else "").strip()
            if val44 != val45:
                field_diffs[k] = {"v44": val44, "v45": val45}
        if field_diffs:
            specs_44 = get_active_pairs(r44, "SPEC", "CON", 30)
            specs_45 = get_active_pairs(r45, "SPEC", "CON", 30)
            keys_44 = get_active_pairs(r44, "KEY", "VAL", 20)
            keys_45 = get_active_pairs(r45, "KEY", "VAL", 20)
            
            differences.append({
                "NO": no,
                "TYPE": "MODIFIED",
                "ADDR_v44": r44.get("ADDR"),
                "ADDR_v45": r45.get("ADDR"),
                "GOTO_v44": r44.get("GOTO"),
                "GOTO_v45": r45.get("GOTO"),
                "REMARKS_v44": r44.get("REMARKS"),
                "REMARKS_v45": r45.get("REMARKS"),
                "SPECS_v44": specs_44,
                "SPECS_v45": specs_45,
                "KEYS_v44": keys_44,
                "KEYS_v45": keys_45,
                "field_diffs": field_diffs
            })

print(f"\n==========================================")
print(f"Total rows in v44: {len(v44_rows)}")
print(f"Total rows in v45: {len(v45_rows)}")
print(f"Total differences: {len(differences)}")
print(f"==========================================\n")

for diff in differences:
    print(f"--- [NO: {diff['NO']}] TYPE: {diff['TYPE']} ---")
    if diff['TYPE'] == "MODIFIED":
        print(f"  ADDR: v44='{diff['ADDR_v44']}' vs v45='{diff['ADDR_v45']}'")
        print(f"  GOTO: v44='{diff['GOTO_v44']}' vs v45='{diff['GOTO_v45']}'")
        print(f"  REMARKS: v44='{diff['REMARKS_v44']}' vs v45='{diff['REMARKS_v45']}'")
        print("  Field changes:")
        for k, v in diff['field_diffs'].items():
            print(f"    - {k}: '{v['v44']}'  ==>  '{v['v45']}'")
        print(f"  v44 SPECS: {diff['SPECS_v44']}")
        print(f"  v45 SPECS: {diff['SPECS_v45']}")
        print(f"  v44 KEYS: {diff['KEYS_v44']}")
        print(f"  v45 KEYS: {diff['KEYS_v45']}")
    elif diff['TYPE'] == "ADDED_IN_V45":
        print(f"  ADDR: '{diff['ADDR']}', GOTO: '{diff['GOTO']}', REMARKS: '{diff['REMARKS']}'")
        print(f"  SPECS: {diff['SPECS']}")
        print(f"  KEYS: {diff['KEYS']}")
    elif diff['TYPE'] == "DELETED_IN_V45":
        print(f"  ADDR: '{diff['ADDR']}', GOTO: '{diff['GOTO']}', REMARKS: '{diff['REMARKS']}'")
        print(f"  SPECS: {diff['SPECS']}")
        print(f"  KEYS: {diff['KEYS']}")
    print()

with open("output_csv/EL_PA103A03_v44_v45_diff.json", "w", encoding="utf-8") as f:
    json.dump(differences, f, ensure_ascii=False, indent=2)
