import json

with open("output_csv/EL_PA103A03_v44_v45_diff.json", "r", encoding="utf-8") as f:
    diffs = json.load(f)

print(f"Total differences found: {len(diffs)}")

real_diffs = []
for d in diffs:
    # Check if the only change is DOUID
    if d["TYPE"] == "MODIFIED":
        fd = d["field_diffs"]
        if list(fd.keys()) == ["DOUID"]:
            continue
    real_diffs.append(d)

print(f"Real functional differences (excluding DOUID only changes): {len(real_diffs)}")

for d in real_diffs:
    print(f"\n==========================================")
    print(f"[NO: {d['NO']}] TYPE: {d['TYPE']}")
    if d["TYPE"] == "MODIFIED":
        print(f"  ADDR: v44='{d.get('ADDR_v44')}' ==> v45='{d.get('ADDR_v45')}'")
        print(f"  GOTO: v44='{d.get('GOTO_v44')}' ==> v45='{d.get('GOTO_v45')}'")
        print(f"  REMARKS: v44='{d.get('REMARKS_v44')}' ==> v45='{d.get('REMARKS_v45')}'")
        print("  Field Diff Details:")
        for k, v in d["field_diffs"].items():
            if k == "DOUID": continue
            print(f"    * {k}: [v44: '{v['v44']}']  ==>  [v45: '{v['v45']}']")
        print(f"  v44 active SPECS: {d['SPECS_v44']}")
        print(f"  v45 active SPECS: {d['SPECS_v45']}")
        print(f"  v44 active KEYS: {d['KEYS_v44']}")
        print(f"  v45 active KEYS: {d['KEYS_v45']}")
    elif d["TYPE"] == "ADDED_IN_V45":
        print(f"  ADDR: {d.get('ADDR')}, GOTO: {d.get('GOTO')}, REMARKS: {d.get('REMARKS')}")
        print(f"  SPECS: {d.get('SPECS')}")
        print(f"  KEYS: {d.get('KEYS')}")
    elif d["TYPE"] == "DELETED_IN_V45":
        print(f"  ADDR: {d.get('ADDR')}, GOTO: {d.get('GOTO')}, REMARKS: {d.get('REMARKS')}")
        print(f"  SPECS: {d.get('SPECS')}")
        print(f"  KEYS: {d.get('KEYS')}")
