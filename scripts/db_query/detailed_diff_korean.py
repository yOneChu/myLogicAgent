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
        # Oracle / API default response is UTF-8 or CP949
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

v44_by_no = {int(r["NO"]): r for r in v44_rows}
v45_by_no = {int(r["NO"]): r for r in v45_rows}

all_nos = sorted(list(set(v44_by_no.keys()) | set(v45_by_no.keys())))

def format_row_summary(r):
    if not r:
        return "EMPTY"
    addr = r.get("ADDR") or ""
    goto = r.get("GOTO") or ""
    remarks = r.get("REMARKS") or ""
    specs = []
    for i in range(1, 31):
        s = r.get(f"SPEC{i}")
        c = r.get(f"CON{i}")
        if s and str(s).strip():
            specs.append(f"{s}={c}")
    keys = []
    for i in range(1, 21):
        k = r.get(f"KEY{i}")
        v = r.get(f"VAL{i}")
        if k and str(k).strip():
            keys.append(f"{k}={v}")
    
    parts = []
    if addr: parts.append(f"ADDR:{addr}")
    if goto: parts.append(f"GOTO:{goto}")
    if remarks: parts.append(f"REMARKS:{remarks}")
    if specs: parts.append(f"SPECS:[{', '.join(specs)}]")
    if keys: parts.append(f"KEYS:[{', '.join(keys)}]")
    return " | ".join(parts)

diff_summary = []

for no in all_nos:
    r44 = v44_by_no.get(no)
    r45 = v45_by_no.get(no)
    
    if r44 is None:
        diff_summary.append({
            "NO": no,
            "TYPE": "ADDED_IN_V45",
            "v44_summary": "",
            "v45_summary": format_row_summary(r45),
            "v45_row": r45
        })
    elif r45 is None:
        diff_summary.append({
            "NO": no,
            "TYPE": "DELETED_IN_V45",
            "v44_summary": format_row_summary(r44),
            "v45_summary": "",
            "v44_row": r44
        })
    else:
        # Check field diffs excluding DOUID
        field_diffs = {}
        for k in r44.keys():
            if k in ["VERSION", "REG_DATE", "USERID", "REG_USER_NAME", "HOUID", "PID", "DOUID"]:
                continue
            v44_val = str(r44.get(k) or "").strip()
            v45_val = str(r45.get(k) or "").strip()
            if v44_val != v45_val:
                field_diffs[k] = {"v44": v44_val, "v45": v45_val}
        
        if field_diffs:
            diff_summary.append({
                "NO": no,
                "TYPE": "MODIFIED",
                "field_diffs": field_diffs,
                "v44_summary": format_row_summary(r44),
                "v45_summary": format_row_summary(r45),
                "v44_row": r44,
                "v45_row": r45
            })

print(f"Total functional diff count: {len(diff_summary)}")

# Group diffs into logical clusters
clusters = {}
for item in diff_summary:
    no = item["NO"]
    if 54 <= no <= 72:
        cat = "NO 54~72 (자재/SPEC 변경 및 REMARKS 수정)"
    elif no == 73:
        cat = "NO 73 (GOTO 분기 수정: STOP -> PICK3)"
    elif 74 <= no <= 140:
        cat = "NO 74~140 (선택조건 조건식 및 수배 자재/비고 변경)"
    elif 141 <= no <= 151:
        cat = "NO 141~151 (PICK3 세부 로직 및 신규 수배 조건 추가)"
    else:
        cat = f"NO {no} (기타)"
    clusters.setdefault(cat, []).append(item)

for cat, items in clusters.items():
    print(f"\n=======================================================")
    print(f"Cluster: {cat} (Count: {len(items)})")
    print(f"=======================================================")
    for d in items:
        print(f"\n[NO {d['NO']}] - TYPE: {d['TYPE']}")
        if d['TYPE'] == "MODIFIED":
            print(f"  v44: {d['v44_summary']}")
            print(f"  v45: {d['v45_summary']}")
            print(f"  Changed Fields ({len(d['field_diffs'])}):")
            for k, v in d['field_diffs'].items():
                print(f"    - {k}: '{v['v44']}' ==> '{v['v45']}'")
        elif d['TYPE'] == "ADDED_IN_V45":
            print(f"  v45 Added: {d['v45_summary']}")
        elif d['TYPE'] == "DELETED_IN_V45":
            print(f"  v44 Deleted: {d['v44_summary']}")

with open("output_csv/EL_PA103A03_v44_v45_korean_diff.json", "w", encoding="utf-8") as f:
    json.dump(diff_summary, f, ensure_ascii=False, indent=2)
