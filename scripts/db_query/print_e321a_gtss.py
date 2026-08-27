import json
import sys
import io

if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

out_path = r'd:\Antigravity_workspace\myLogicAgent\output_e321a_gtss.json'
with open(out_path, 'r', encoding='utf-8') as f:
    data = json.load(f)

print(f"Total rows: {len(data)}")
for r in data:
    rem = str(r.get('REMARKS', ''))
    val = str(r.get('VAL1', ''))
    if '4672' in rem or 'GTSS' in rem or 'GTSS' in val:
        print(f"NO {r.get('NO')}: ADDR='{r.get('ADDR')}' | SPEC1='{r.get('SPEC1')}', CON1='{r.get('CON1')}' | SPEC2='{r.get('SPEC2')}', CON2='{r.get('CON2')}' | KEY1='{r.get('KEY1')}', VAL1='{r.get('VAL1')}' | REMARKS='{rem}'")
