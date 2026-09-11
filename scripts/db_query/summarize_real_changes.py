import json

with open("output_csv/EL_PE324A_v44_v45_diff_summary.json", "r", encoding="utf-8") as f:
    diffs = json.load(f)

print(f"Total Changed NOs count: {len(diffs)}")

changed_nos = []
for d in diffs:
    no = d["NO"]
    t = d["TYPE"]
    if t in ("ADDED_IN_V45", "DELETED_IN_V45"):
        changed_nos.append((no, t, []))
    else:
        # Check if DOUID is the only changed field
        details = d.get("details", [])
        real_changes = [det for det in details if det["field"] != "DOUID"]
        if real_changes:
            changed_nos.append((no, t, real_changes))

print(f"NOs with REAL (non-DOUID) changes count: {len(changed_nos)}")
for no, t, real_changes in changed_nos:
    print(f"\nNO {no} ({t}):")
    for rc in real_changes:
        print(f"  {rc['field']}: {rc['v44']} ==> {rc['v45']}")
    if t in ("ADDED_IN_V45", "DELETED_IN_V45"):
        print(f"  {d}")
