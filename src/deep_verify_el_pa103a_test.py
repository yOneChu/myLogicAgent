#!/usr/bin/env python3
"""
EL_PA103A 테스트 버전 심층 정밀 검사 스크립트

output_csv/EL_PA103A_test.csv 파일의 전체 1,169행에 대하여
구획별 흐름(ADDR/GOTO), KEY-VAL 빈값 카운트 그룹화,
SPEC만 존재하는 주요 특성코드 집계 등을 심층 분석합니다.
"""

import csv
import sys
from collections import Counter, defaultdict
from pathlib import Path

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')


def analyze_test_version_details(csv_path: Path):
    with open(csv_path, 'r', encoding='utf-8-sig') as f:
        rows = list(csv.DictReader(f))

    print(f"=== PID EL_PA103A 테스트 버전 (v-1) 심층 분석 ===")
    print(f"총 행 수: {len(rows)} 행\n")

    # 1. ADDR 및 GOTO 구조 분석
    addrs = Counter()
    gotos = Counter()
    addr_rows = defaultdict(list)

    current_addr = "MAIN_DEFAULT"
    for r in rows:
        no = r.get('NO', '')
        addr = r.get('ADDR', '-').strip()
        goto = r.get('GOTO', '-').strip()

        if addr != '' and addr != '-':
            current_addr = addr
            addrs[addr] += 1
        
        addr_rows[current_addr].append(no)

        if goto != '' and goto != '-':
            gotos[goto] += 1

    print("[1] ADDR 구획별 행 수 분포:")
    for a, count in addrs.items():
        print(f"  - ADDR '{a}': {count} 개 행 (시작 행 NO: {addr_rows[a][0]})")
    print()

    print("[2] GOTO 분기 목적지 사용 카운트:")
    for g, count in gotos.items():
        print(f"  - GOTO '{g}': {count} 회 호출")
    print()

    # 2. KEY만 있고 VAL이 공백인 심각 오류 그룹화
    key_empty_val_counter = Counter()
    key_empty_val_examples = defaultdict(list)

    for r in rows:
        no = r.get('NO', '')
        for i in range(1, 21):
            k = r.get(f'KEY{i}', '-').strip()
            v = r.get(f'VAL{i}', '-').strip()

            if (k != '' and k != '-') and (v == '' or v == '-'):
                key_empty_val_counter[k] += 1
                if len(key_empty_val_examples[k]) < 5:
                    key_empty_val_examples[k].append(no)

    print("[3] KEY만 있고 VAL이 공백인 미완성 산출 항목 (총 274건 분석):")
    for k, count in key_empty_val_counter.most_common():
        ex = ", ".join(key_empty_val_examples[k])
        print(f"  - KEY '{k}': {count} 건 누락 (대표 행 NO: {ex})")
    print()

    # 3. SPEC만 있고 CON이 빈 칸인 특성코드 통계
    spec_empty_con_counter = Counter()
    for r in rows:
        for i in range(1, 31):
            s = r.get(f'SPEC{i}', '-').strip()
            c = r.get(f'CON{i}', '-').strip()

            if (s != '' and s != '-') and (c == '' or c == '-'):
                spec_empty_con_counter[s] += 1

    print("[4] SPEC만 있고 CON이 비어 있는 상위 특성코드 TOP 10 (총 4,030건 분석):")
    for s, count in spec_empty_con_counter.most_common(10):
        print(f"  - SPEC '{s}': {count} 회 등장 (CON 누락/확인필요)")
    print()

    # 4. KEY=CALL 연동 로직 PID 호출 확인
    calls = []
    for r in rows:
        no = r.get('NO', '')
        for i in range(1, 21):
            k = r.get(f'KEY{i}', '-').strip()
            v = r.get(f'VAL{i}', '-').strip()
            if k == 'CALL':
                calls.append((no, v))

    print(f"[5] CALL 키워드를 통한 하위 PID 호출 ({len(calls)}건):")
    for no, val in calls:
        print(f"  - [NO: {no}] CALL PID -> '{val}'")
    print()


if __name__ == "__main__":
    project_root = Path(__file__).resolve().parent.parent
    target_csv = project_root / "output_csv" / "EL_PA103A_test.csv"
    analyze_test_version_details(target_csv)
