#!/usr/bin/env python3
"""
PID EL_PA103A 테스트 버전에서 문법적 문제(오류)가 있는 라인(NO 번호) 전수 추출 스크립트
"""

import csv
import sys
from collections import defaultdict
from pathlib import Path

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')


def extract_problematic_lines():
    project_root = Path(__file__).resolve().parent.parent
    target_csv = project_root / "output_csv" / "EL_PA103A_test.csv"

    with open(target_csv, 'r', encoding='utf-8-sig') as f:
        rows = list(csv.DictReader(f))

    # 1. KEY 선언 후 VAL 공백
    key_no_val_nos = defaultdict(list)

    # 2. 전체 열 100% 동일 중복행
    full_row_tuples = {}
    full_dup_nos = []

    # 3. 조건열 100% 동일 중복행
    spec_con_tuples = {}
    spec_con_dup_nos = []

    for r in rows:
        no = r.get('NO', '')

        # KEY/VAL
        for i in range(1, 21):
            k = r.get(f'KEY{i}', '-').strip()
            v = r.get(f'VAL{i}', '-').strip()
            if (k != '' and k != '-') and (v == '' or v == '-'):
                key_no_val_nos[k].append(no)

        # Full Row Tuple
        full_list = []
        for i in range(1, 31):
            full_list.append((r.get(f'SPEC{i}', '-').strip(), r.get(f'CON{i}', '-').strip()))
        for i in range(1, 21):
            full_list.append((r.get(f'KEY{i}', '-').strip(), r.get(f'VAL{i}', '-').strip()))
        
        full_tuple = tuple(full_list)
        if not all(k == '-' and v == '-' for k, v in full_tuple):
            if full_tuple in full_row_tuples:
                full_dup_nos.append((no, full_row_tuples[full_tuple]))
            else:
                full_row_tuples[full_tuple] = no

        # SPEC/CON Tuple
        spec_con_tuple = tuple((r.get(f'SPEC{i}', '-').strip(), r.get(f'CON{i}', '-').strip()) for i in range(1, 31))
        if not all(s == '-' and c == '-' for s, c in spec_con_tuple):
            if spec_con_tuple in spec_con_tuples:
                spec_con_dup_nos.append((no, spec_con_tuples[spec_con_tuple]))
            else:
                spec_con_tuples[spec_con_tuple] = no

    print("=== PID EL_PA103A 테스트 버전 문제 라인(NO 번호) 추출 ===")
    
    print("\n[1] VAL 산출값 누락 라인 (총 274건):")
    for k, nos in key_no_val_nos.items():
        print(f"  - KEY '{k}' ({len(nos)}건): NO {', '.join(nos)}")

    print(f"\n[2] 전체 열 100% 완전 중복 라인 (총 {len(full_dup_nos)}건):")
    print(f"  - 라인 번호 (NO): {', '.join([d[0] for d in full_dup_nos])}")

    spec_only_dup = [d for d in spec_con_dup_nos if d not in full_dup_nos]
    print(f"\n[3] 조건열(SPEC/CON)만 100% 중복 라인 (추가 {len(spec_only_dup)}건):")
    print(f"  - 라인 번호 (NO): {', '.join([d[0] for d in spec_only_dup])}")


if __name__ == "__main__":
    extract_problematic_lines()
