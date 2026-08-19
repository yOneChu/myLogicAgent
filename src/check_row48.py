#!/usr/bin/env python3
"""
EL_PA103A 테스트 버전 NO 48행 상세 검사 및 전체 행 대상 중복/유사성 분석 스크립트
"""

import csv
import sys
from pathlib import Path

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')


def check_row48():
    project_root = Path(__file__).resolve().parent.parent
    target_csv = project_root / "output_csv" / "EL_PA103A_test.csv"

    with open(target_csv, 'r', encoding='utf-8-sig') as f:
        rows = list(csv.DictReader(f))

    r48 = next((r for r in rows if r['NO'] == '48'), None)
    
    print("=== NO 48 행의 전체 채워진 열 데이터 ===")
    for k, v in r48.items():
        if v and v != '-':
            print(f"  {k}: '{v}'")
    print()

    # NO 48과 완전히 동일한 다른 행이 존재하는지 전수 비교 (모든 열 또는 SPEC/CON/KEY/VAL/ADDR/GOTO/REMARKS)
    print("=== NO 48과 완전히 동일한 행 찾기 (모든 열 비교) ===")
    exact_matches = []
    spec_con_matches = []
    all_col_except_no_matches = []

    cols_to_check = [k for k in r48.keys() if k != 'NO']

    for r in rows:
        no = r['NO']
        if no == '48':
            continue

        # 1. NO 제외한 모든 열 비교
        if all(r.get(c, '-').strip() == r48.get(c, '-').strip() for c in cols_to_check):
            all_col_except_no_matches.append(no)

        # 2. SPEC1~30, CON1~30 조건열 비교
        spec_con_same = True
        for i in range(1, 31):
            if r.get(f'SPEC{i}', '-').strip() != r48.get(f'SPEC{i}', '-').strip() or \
               r.get(f'CON{i}', '-').strip() != r48.get(f'CON{i}', '-').strip():
                spec_con_same = False
                break
        if spec_con_same:
            spec_con_matches.append(no)

    print(f"NO 48과 [모든 열(ADDR, GOTO, REMARKS, SPEC, CON, KEY, VAL)] 완전 동일 행: {all_col_except_no_matches}")
    print(f"NO 48과 [SPEC1~30, CON1~30 조건] 완전 동일 행: {spec_con_matches}")
    print()

    print("=== NO 40 ~ NO 55 행 주변 내용 ===")
    for r in rows:
        no = int(r['NO'])
        if 40 <= no <= 55:
            specs = [f"SPEC{i}:{r[f'SPEC{i}']}=CON{i}:{r[f'CON{i}']}" for i in range(1, 31) if r[f'SPEC{i}'] != '-']
            keys = [f"KEY{i}:{r[f'KEY{i}']}=VAL{i}:{r[f'VAL{i}']}" for i in range(1, 21) if r[f'KEY{i}'] != '-']
            print(f"NO {r['NO']:>3} | ADDR:{r.get('ADDR','-'):<10} | GOTO:{r.get('GOTO','-'):<5} | REMARKS:{r.get('REMARKS','-'):<15} | SPEC:{specs} | KEY:{keys}")


if __name__ == "__main__":
    check_row48()
