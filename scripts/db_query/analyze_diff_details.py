import json

with open("output_csv/EL_PE324A_v44_v45_diff_summary.json", "r", encoding="utf-8") as f:
    diffs = json.load(f)

print(f"Total Diff Entries: {len(diffs)}")

added = [d for d in diffs if d["TYPE"] == "ADDED_IN_V45"]
deleted = [d for d in diffs if d["TYPE"] == "DELETED_IN_V45"]
modified = [d for d in diffs if d["TYPE"] == "MODIFIED"]

print(f"Added rows in v45: {len(added)} (NOs: {[d['NO'] for d in added]})")
print(f"Deleted rows in v45: {len(deleted)} (NOs: {[d['NO'] for d in deleted]})")
print(f"Modified rows: {len(modified)}")

# Analyze modified details
mod_summary = {}
for m in modified:
    no = m["NO"]
    details = m.get("details", [])
    fields_changed = [d["field"] for d in details]
    mod_summary[no] = details

print("\n--- Detailed Summary of Modifications ---")
for no, details in mod_summary.items():
    print(f"\n[NO {no}]")
    for d in details:
        print(f"  Field {d['field']}: '{d['v44']}' => '{d['v45']}'")
