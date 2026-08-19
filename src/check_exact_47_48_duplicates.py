#!/usr/bin/env python3
import csv
import sys
from pathlib import Path

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

project_root = Path(__file__).resolve().parent.parent
target_csv = project_root / "output_csv" / "EL_PA103A_test.csv"

with open(target_csv, 'r', encoding='utf-8-sig') as f:
    rows = list(csv.DictReader(f))

for target_no in ('47', '48'):
    r_target = next(r for r in rows if r['NO'] == target_no)
    target_spec_con = tuple((r_target.get(f'SPEC{i}', '-').strip(), r_target.get(f'CON{i}', '-').strip()) for i in range(1, 31))

    same_spec_con = []
    for r in rows:
        if r['NO'] == target_no:
            continue
        spec_con = tuple((r.get(f'SPEC{i}', '-').strip(), r.get(f'CON{i}', '-').strip()) for i in range(1, 31))
        if spec_con == target_spec_con:
            same_spec_con.append(r['NO'])

    print(f"NO {target_no}행과 SPEC1~30, CON1~30 조건식이 100% 동일한 다른 행: {same_spec_con if same_spec_con else '없음'}")
