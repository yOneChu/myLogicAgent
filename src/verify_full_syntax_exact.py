#!/usr/bin/env python3
"""
PLM 로직 Editor 문법 규칙 (.agents/rules/logic-syntax.md) 기준 전수 검증 스크립트

규칙 5절:
1행에서 마지막행까지 한 라인의 값 SPEC1~30, CON1~30, KEY1~20, VAL1~20 열의 값과 동일한 행이 있으면 문법에 어긋난다.
"""

import csv
import sys
from collections import defaultdict
from pathlib import Path

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')


def verify_logic_syntax_strict(csv_path: Path):
    with open(csv_path, 'r', encoding='utf-8-sig') as f:
        rows = list(csv.DictReader(f))

    print(f"=== PLM 로직 Editor 문법 규칙 (.agents/rules/logic-syntax.md) 기준 검증 ===")
    print(f"검증 대상 파일: {csv_path} (총 {len(rows)} 행)\n")

    # 1. SPEC1~30, CON1~30, KEY1~20, VAL1~20 전체 열 100% 동일행 검사 (규칙 5절)
    full_row_tuples = {}
    full_duplicates = []

    # 2. SPEC1~30, CON1~30 조건열 100% 동일행 검사
    spec_con_tuples = {}
    spec_con_duplicates = []

    # 3. KEY만 존재하고 VAL이 공백인 경우
    key_without_val = []

    # 4. SPEC이 공백인데 CON이 존재하는 경우
    spec_missing = []

    # 5. SPEC만 존재하고 CON이 공백인 경우 ([확인 필요])
    confirm_needed = []

    # 6. GOTO 목적지 라벨 유효성
    valid_addrs = {r.get('ADDR', '').strip() for r in rows if r.get('ADDR', '').strip() not in ('', '-')}
    unresolved_gotos = []

    for r in rows:
        no = r.get('NO', '')

        # (1) 전체 SPEC/CON/KEY/VAL 튜플
        row_tuple_list = []
        for i in range(1, 31):
            row_tuple_list.append((r.get(f'SPEC{i}', '-').strip(), r.get(f'CON{i}', '-').strip()))
        for i in range(1, 21):
            row_tuple_list.append((r.get(f'KEY{i}', '-').strip(), r.get(f'VAL{i}', '-').strip()))
        
        full_tuple = tuple(row_tuple_list)
        is_all_empty = all(k == '-' and v == '-' for k, v in full_tuple)

        if not is_all_empty:
            if full_tuple in full_row_tuples:
                full_duplicates.append((no, full_row_tuples[full_tuple]))
            else:
                full_row_tuples[full_tuple] = no

        # (2) SPEC/CON 조건 튜플
        spec_con_tuple = tuple((r.get(f'SPEC{i}', '-').strip(), r.get(f'CON{i}', '-').strip()) for i in range(1, 31))
        is_spec_con_empty = all(s == '-' and c == '-' for s, c in spec_con_tuple)

        if not is_spec_con_empty:
            if spec_con_tuple in spec_con_tuples:
                spec_con_duplicates.append((no, spec_con_tuples[spec_con_tuple]))
            else:
                spec_con_tuples[spec_con_tuple] = no

        # (3) KEY/VAL 짝 검사
        for i in range(1, 21):
            k = r.get(f'KEY{i}', '-').strip()
            v = r.get(f'VAL{i}', '-').strip()
            if (k != '' and k != '-') and (v == '' or v == '-'):
                key_without_val.append((no, f"KEY{i}:{k}"))

        # (4) SPEC/CON 짝 검사
        for i in range(1, 31):
            s = r.get(f'SPEC{i}', '-').strip()
            c = r.get(f'CON{i}', '-').strip()
            if (s == '' or s == '-') and (c != '' and c != '-'):
                spec_missing.append((no, f"CON{i}:{c}"))
            elif (s != '' and s != '-') and (c == '' or c == '-'):
                confirm_needed.append((no, f"SPEC{i}:{s}"))

        # (5) GOTO 검사
        goto = r.get('GOTO', '-').strip()
        if goto not in ('', '-', 'STOP') and goto not in valid_addrs:
            unresolved_gotos.append((no, goto))

    print("[검증 결과 요약]")
    print(f"1. 전체 열 (SPEC1~30, CON1~30, KEY1~20, VAL1~20) 100% 동일 행: {len(full_duplicates)} 건")
    if full_duplicates:
        for dup in full_duplicates:
            print(f"   - 행 {dup[0]} (행 {dup[1]} 기준 100% 동일 중복)")

    print(f"\n2. 조건열 (SPEC1~30, CON1~30) 100% 동일 행: {len(spec_con_duplicates)} 건")
    print(f"3. KEY 선언 후 VAL(산출값) 공백 문법 오류: {len(key_without_val)} 건")
    print(f"4. SPEC 공백인데 CON만 존재하는 문법 오류: {len(spec_missing)} 건")
    print(f"5. GOTO 목적지 라벨 오류: {len(unresolved_gotos)} 건")
    print(f"6. [확인 필요] SPEC만 존재하고 CON 공백 사양: {len(confirm_needed)} 건")


if __name__ == "__main__":
    project_root = Path(__file__).resolve().parent.parent
    target_csv = project_root / "output_csv" / "EL_PA103A_test.csv"
    verify_logic_syntax_strict(target_csv)
