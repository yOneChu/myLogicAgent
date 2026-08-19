#!/usr/bin/env python3
"""
EL_PA103A 테스트 버전 중복 행 전수 추출 스크립트

output_csv/EL_PA103A_test.csv 파일에서
SPEC1~30, CON1~30 조건식이 동일한 중복 행 70건의
중복 행 번호(NO)와 원본 비교 행 번호를 전수 조사하여 반환합니다.
"""

import csv
import sys
from pathlib import Path

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')


def find_duplicates(csv_path: Path):
    with open(csv_path, 'r', encoding='utf-8-sig') as f:
        rows = list(csv.DictReader(f))

    seen_spec_con = {}
    duplicates = []

    for row in rows:
        no = row.get('NO', '')
        spec_con_tuple = tuple((row.get(f'SPEC{i}', '-').strip(), row.get(f'CON{i}', '-').strip()) for i in range(1, 31))
        
        is_all_empty = all(s == '-' and c == '-' for s, c in spec_con_tuple)
        if is_all_empty:
            continue

        if spec_con_tuple in seen_spec_con:
            orig_no = seen_spec_con[spec_con_tuple]
            # 비어있지 않은 SPEC-CON 요약
            specs = [f"SPEC{i}:{s}=CON{i}:{c}" for i, (s, c) in enumerate(spec_con_tuple, 1) if s != '-' or c != '-']
            spec_str = ", ".join(specs[:3]) + ("..." if len(specs) > 3 else "")
            duplicates.append({
                'NO': no,
                'orig_NO': orig_no,
                'summary': spec_str
            })
        else:
            seen_spec_con[spec_con_tuple] = no

    print(f"총 발견된 중복 행: {len(duplicates)} 건\n")
    print("| 중복 행 번호 (NO) | 원본 최초 행 (NO) | 조건식 요약 |")
    print("|---|---|---|")
    for dup in duplicates:
        print(f"| 행 {dup['NO']} | 행 {dup['orig_NO']} 기준 중복 | `{dup['summary']}` |")


if __name__ == "__main__":
    project_root = Path(__file__).resolve().parent.parent
    target_csv = project_root / "output_csv" / "EL_PA103A_test.csv"
    find_duplicates(target_csv)
