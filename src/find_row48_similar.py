#!/usr/bin/env python3
"""
NO 48행과 조건 및 산출이 비슷한/중복된 모든 행 분석 스크립트
"""

import csv
import sys
from pathlib import Path

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')


def find_similar_to_48():
    project_root = Path(__file__).resolve().parent.parent
    target_csv = project_root / "output_csv" / "EL_PA103A_test.csv"

    with open(target_csv, 'r', encoding='utf-8-sig') as f:
        rows = list(csv.DictReader(f))

    r48 = next(r for r in rows if r['NO'] == '48')

    print("=== NO 48행의 사양 조건 및 산출값 ===")
    for k, v in r48.items():
        if v and v != '-':
            print(f"  {k}: '{v}'")
    print()

    print("=== NO 48행과 유사/중복 가능성이 있는 행 탐색 ===")
    for r in rows:
        no = r['NO']
        if no == '48':
            continue

        # 1. SPEC/CON 차이점
        diff_spec_con = []
        for i in range(1, 31):
            s1, c1 = r48.get(f'SPEC{i}', '-').strip(), r48.get(f'CON{i}', '-').strip()
            s2, c2 = r.get(f'SPEC{i}', '-').strip(), r.get(f'CON{i}', '-').strip()
            if (s1, c1) != (s2, c2):
                diff_spec_con.append((i, f"s1:{s1}={c1}", f"s2:{s2}={c2}"))

        # 2. KEY/VAL 차이점
        diff_key_val = []
        for i in range(1, 21):
            k1, v1 = r48.get(f'KEY{i}', '-').strip(), r48.get(f'VAL{i}', '-').strip()
            k2, v2 = r.get(f'KEY{i}', '-').strip(), r.get(f'VAL{i}', '-').strip()
            if (k1, v1) != (k2, v2):
                diff_key_val.append((i, f"k1:{k1}={v1}", f"k2:{k2}={v2}"))

        # 조건이 거의 일치하는 행 (차이가 2개 이하인 경우)
        if len(diff_spec_con) <= 2:
            print(f"-> NO {no:>4} 행: SPEC/CON 차이 {len(diff_spec_con)}개, KEY/VAL 차이 {len(diff_key_val)}개")
            for d in diff_spec_con:
                print(f"     SPEC{d[0]} 차이: {d[1]} vs {d[2]}")
            for d in diff_key_val[:3]:
                print(f"     KEY{d[0]} 차이: {d[1]} vs {d[2]}")
            print()


if __name__ == "__main__":
    find_similar_to_48()
