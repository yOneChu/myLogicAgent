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

print("Fetching header info...")
header_sql = """
SELECT H.PID, H.VERSION, H.HOUID, H.REG_DATE, H.USERID,
       (SELECT F.MD$DESC FROM FUSER$SF F WHERE F.MD$NUMBER = H.USERID) AS REG_USER_NAME
  FROM HDEL_DEFAULT.VARIANT_H H
 WHERE H.HOUID IN (1264930, 1304564)
"""
headers_data = fetch_data(header_sql)
header_map = {int(r["HOUID"]): r for r in headers_data}

v44_h_info = header_map.get(1264930, {})
v45_h_info = header_map.get(1304564, {})

print("Fetching v44 detail (HOUID: 1264930)...")
v44_sql = "SELECT '44' AS VERSION, D.* FROM HDEL_DEFAULT.VARIANT_D D WHERE D.HOUID = 1264930 ORDER BY TO_NUMBER(D.NO)"
v44_rows = fetch_data(v44_sql)
print(f"v44 fetched: {len(v44_rows)} rows")

print("Fetching v45 detail (HOUID: 1304564)...")
v45_sql = "SELECT '45' AS VERSION, D.* FROM HDEL_DEFAULT.VARIANT_D D WHERE D.HOUID = 1304564 ORDER BY TO_NUMBER(D.NO)"
v45_rows = fetch_data(v45_sql)
print(f"v45 fetched: {len(v45_rows)} rows")

# Attach header info to each row
for r in v44_rows:
    r["PID"] = v44_h_info.get("PID", "EL_PE324A")
    r["REG_DATE"] = v44_h_info.get("REG_DATE")
    r["USERID"] = v44_h_info.get("USERID")
    r["REG_USER_NAME"] = v44_h_info.get("REG_USER_NAME")

for r in v45_rows:
    r["PID"] = v45_h_info.get("PID", "EL_PE324A")
    r["REG_DATE"] = v45_h_info.get("REG_DATE")
    r["USERID"] = v45_h_info.get("USERID")
    r["REG_USER_NAME"] = v45_h_info.get("REG_USER_NAME")

data = v44_rows + v45_rows

os.makedirs("output_csv", exist_ok=True)
os.makedirs("output_excel", exist_ok=True)

if data:
    headers = list(data[0].keys())
    with open("output_csv/EL_PE324A_v44_v45.csv", "w", newline="", encoding="utf-8-sig") as f:
        writer = csv.DictWriter(f, fieldnames=headers)
        writer.writeheader()
        writer.writerows(data)

print(f"\nv44 Header: REG_DATE={v44_h_info.get('REG_DATE')}, USERID={v44_h_info.get('USERID')}, USER_NAME={v44_h_info.get('REG_USER_NAME')}")
print(f"v45 Header: REG_DATE={v45_h_info.get('REG_DATE')}, USERID={v45_h_info.get('USERID')}, USER_NAME={v45_h_info.get('REG_USER_NAME')}\n")

# Index by NO
v44_by_no = {int(r["NO"]): r for r in v44_rows}
v45_by_no = {int(r["NO"]): r for r in v45_rows}

all_nos = sorted(list(set(v44_by_no.keys()) | set(v45_by_no.keys())))

differences = []
ignore_fields = {"VERSION", "REG_DATE", "USERID", "REG_USER_NAME", "HOUID", "PID"}

for no in all_nos:
    r44 = v44_by_no.get(no)
    r45 = v45_by_no.get(no)
    
    if r44 is None:
        differences.append({"NO": no, "TYPE": "ADDED_IN_V45", "v44": None, "v45": r45})
    elif r45 is None:
        differences.append({"NO": no, "TYPE": "DELETED_IN_V45", "v44": r44, "v45": None})
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
            differences.append({"NO": no, "TYPE": "MODIFIED", "field_diffs": field_diffs, "v44": r44, "v45": r45})

print(f"--- Total Differences Count: {len(differences)} ---")

diff_report = []

for diff in differences:
    print(f"\n==========================================")
    print(f"[NO: {diff['NO']}] TYPE: {diff['TYPE']}")
    item = {"NO": diff['NO'], "TYPE": diff['TYPE']}
    if diff['TYPE'] == "MODIFIED":
        r44 = diff['v44']
        r45 = diff['v45']
        print(f"  v44 ADDR: {r44.get('ADDR')}, REMARKS: {r44.get('REMARKS')}")
        print(f"  v45 ADDR: {r45.get('ADDR')}, REMARKS: {r45.get('REMARKS')}")
        item["ADDR_v44"] = r44.get('ADDR')
        item["ADDR_v45"] = r45.get('ADDR')
        item["REMARKS_v44"] = r44.get('REMARKS')
        item["REMARKS_v45"] = r45.get('REMARKS')
        item["details"] = []
        for k, v in diff['field_diffs'].items():
            print(f"    - Field {k}: [v44: '{v['v44']}']  ==>  [v45: '{v['v45']}']")
            item["details"].append({"field": k, "v44": v['v44'], "v45": v['v45']})
    elif diff['TYPE'] == "ADDED_IN_V45":
        r = diff['v45']
        print(f"  Added row in v45:")
        print(f"    ADDR: {r.get('ADDR')}, GOTO: {r.get('GOTO')}, REMARKS: {r.get('REMARKS')}")
        specs = [f"{r.get(f'SPEC{i}')}={r.get(f'CON{i}')}" for i in range(1, 31) if r.get(f'SPEC{i}') is not None and str(r.get(f'SPEC{i}')).strip() != '']
        keys = [f"{r.get(f'KEY{i}')}={r.get(f'VAL{i}')}" for i in range(1, 21) if r.get(f'KEY{i}') is not None and str(r.get(f'KEY{i}')).strip() != '']
        print(f"    SPECS: {', '.join(specs)}")
        print(f"    KEYS: {', '.join(keys)}")
        item["ADDR"] = r.get('ADDR')
        item["GOTO"] = r.get('GOTO')
        item["REMARKS"] = r.get('REMARKS')
        item["SPECS"] = ', '.join(specs)
        item["KEYS"] = ', '.join(keys)
    elif diff['TYPE'] == "DELETED_IN_V45":
        r = diff['v44']
        print(f"  Deleted row in v45:")
        print(f"    ADDR: {r.get('ADDR')}, GOTO: {r.get('GOTO')}, REMARKS: {r.get('REMARKS')}")
        specs = [f"{r.get(f'SPEC{i}')}={r.get(f'CON{i}')}" for i in range(1, 31) if r.get(f'SPEC{i}') is not None and str(r.get(f'SPEC{i}')).strip() != '']
        keys = [f"{r.get(f'KEY{i}')}={r.get(f'VAL{i}')}" for i in range(1, 21) if r.get(f'KEY{i}') is not None and str(r.get(f'KEY{i}')).strip() != '']
        print(f"    SPECS: {', '.join(specs)}")
        print(f"    KEYS: {', '.join(keys)}")
        item["ADDR"] = r.get('ADDR')
        item["GOTO"] = r.get('GOTO')
        item["REMARKS"] = r.get('REMARKS')
        item["SPECS"] = ', '.join(specs)
        item["KEYS"] = ', '.join(keys)
    diff_report.append(item)

with open("output_csv/EL_PE324A_v44_v45_diff_summary.json", "w", encoding="utf-8") as f:
    json.dump(diff_report, f, ensure_ascii=False, indent=2)
