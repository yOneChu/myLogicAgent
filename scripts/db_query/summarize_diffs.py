import json

with open("output_csv/EL_PA103A03_v44_v45_diff.json", "r", encoding="utf-8") as f:
    diffs = json.load(f)

real_diffs = []
for d in diffs:
    if d["TYPE"] == "MODIFIED":
        fd = d["field_diffs"]
        if list(fd.keys()) == ["DOUID"]:
            continue
    real_diffs.append(d)

print(f"Total functional differences count: {len(real_diffs)}")
changed_nos = [d["NO"] for d in real_diffs]
print("Changed NOs:", changed_nos)

print("\n--- Summary per NO ---")
for d in real_diffs:
    no = d["NO"]
    t = d["TYPE"]
    if t == "MODIFIED":
        fields = [k for k in d["field_diffs"].keys() if k != "DOUID"]
        print(f"NO {no:3d} [MODIFIED]: Fields changed: {', '.join(fields)}")
        if "REMARKS" in fields:
            print(f"        REMARKS: '{d['REMARKS_v44']}' ==> '{d['REMARKS_v45']}'")
        if "ADDR" in fields:
            print(f"        ADDR: '{d['ADDR_v44']}' ==> '{d['ADDR_v45']}'")
        if "GOTO" in fields:
            print(f"        GOTO: '{d['GOTO_v44']}' ==> '{d['GOTO_v45']}'")
    elif t == "ADDED_IN_V45":
        print(f"NO {no:3d} [ADDED ]: ADDR='{d.get('ADDR')}', REMARKS='{d.get('REMARKS')}'")
    elif t == "DELETED_IN_V45":
        print(f"NO {no:3d} [DELETED]: ADDR='{d.get('ADDR')}', REMARKS='{d.get('REMARKS')}'")
