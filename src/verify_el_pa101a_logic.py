#!/usr/bin/env python3
"""
EL_PA101A PID 로직 정합성 및 문법 규칙 검증 스크립트.

이 스크립트는 logic-syntax.md 및 logic-BOM정합성_작성수정_rule.md에 정의된 규칙에 따라
PLM 로직 데이터를 검증하고 결과를 요약 보고서 및 상세 콘솔 출력으로 제공합니다.
"""

import csv
import sys
from collections import defaultdict
from pathlib import Path

# 표준 출력 인코딩을 UTF-8로 설정
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')


def load_csv_data(csv_path: Path) -> list[dict[str, str]]:
    """
    CSV 파일 경로를 입력받아 DictReader 형태의 행 리스트로 반환하는 함수.
    
    :param csv_path: 검증할 CSV 파일 경로
    :param return: 로직 행 정보가 담긴 딕셔너리 리스트
    """
    with open(csv_path, 'r', encoding='utf-8-sig') as f:
        reader = csv.DictReader(f)
        return list(reader)


def verify_el_pa101a_syntax(rows: list[dict[str, str]]) -> tuple[list[dict], list[dict], dict]:
    """
    EL_PA101A 로직 데이터의 문법 및 정합성 검칙을 검증하는 메인 검증 함수.
    
    검사 항목:
    1. SPEC/CON 짝 규칙:
       - SPEC이 공백인데 CON에 값이 있으면 문법 오류 (SPEC_MISSING)
       - SPEC만 있고 CON이 비어 있으면 [확인 필요] (SPEC_WITHOUT_CON)
    2. KEY/VAL 짝 규칙:
       - KEY만 존재하고 VAL이 비어 있는 경우 (KEY_WITHOUT_VAL)
       - VAL만 존재하고 KEY가 비어 있는 경우 (VAL_WITHOUT_KEY)
    3. GOTO 분기 라벨 유효성:
       - GOTO가 지정된 라벨이 전체 ADDR 선언에 존재하는지 검사 (UNRESOLVED_GOTO)
    4. 행 중복 검사 (logic-syntax.md 핵심 규칙):
       - ADDR, REMARKS를 제외한 나머지 열(SPEC1~30, CON1~30, KEY1~20, VAL1~20, GOTO)의 모든 조합이 동일한 중복행 (DUPLICATE_FULL_ROW)
       - SPEC1~30, CON1~30 조건 항목 조합만 완벽히 동일한 조건 중복행 (DUPLICATE_SPEC_CON)
    
    :param rows: CSV에서 읽어온 로직 행 리스트
    :return: (문법오류 리스트, 확인필요 리스트, 통계 딕셔너리)
    """
    syntax_errors = []
    confirm_needed = []

    # 전체 행에 선언된 유효 ADDR 라벨 수집
    valid_addrs = set()
    for r in rows:
        addr = r.get('ADDR', '').strip()
        if addr and addr != '-':
            valid_addrs.add(addr)

    # 중복 검사를 위한 해시맵
    seen_full_rows = {}
    seen_spec_con_tuples = {}

    for row in rows:
        no = row.get('NO', '').strip()

        # 1. SPEC / CON 짝 및 형식 검사
        for i in range(1, 31):
            s = row.get(f'SPEC{i}', '-').strip()
            c = row.get(f'CON{i}', '-').strip()

            is_s_empty = (s == '' or s == '-')
            is_c_empty = (c == '' or c == '-')

            if is_s_empty and not is_c_empty:
                syntax_errors.append({
                    'NO': no,
                    'rule': 'SPEC_MISSING',
                    'msg': f"SPEC{i}가 공백인데 CON{i}('{c}')에 값이 입력됨 [문법 오류]"
                })
            elif not is_s_empty and is_c_empty:
                confirm_needed.append({
                    'NO': no,
                    'spec': s,
                    'msg': f"SPEC{i}('{s}')만 정의되고 CON{i}가 비어 있음 [확인 필요]"
                })

        # 2. KEY / VAL 짝 검사
        for i in range(1, 21):
            k = row.get(f'KEY{i}', '-').strip()
            v = row.get(f'VAL{i}', '-').strip()

            is_k_empty = (k == '' or k == '-')
            is_v_empty = (v == '' or v == '-')

            if not is_k_empty and is_v_empty:
                syntax_errors.append({
                    'NO': no,
                    'rule': 'KEY_WITHOUT_VAL',
                    'key': k,
                    'msg': f"KEY{i}('{k}')만 정의되고 산출값 VAL{i}가 공백임 [문법 오류]"
                })
            elif is_k_empty and not is_v_empty:
                syntax_errors.append({
                    'NO': no,
                    'rule': 'VAL_WITHOUT_KEY',
                    'val': v,
                    'msg': f"KEY{i}는 공백인데 산출값 VAL{i}('{v}')가 지정됨 [문법 오류]"
                })

        # 3. GOTO 분기 라벨 유효성 검사
        goto = row.get('GOTO', '-').strip()
        if goto and goto not in ('-', 'STOP') and goto not in valid_addrs:
            syntax_errors.append({
                'NO': no,
                'rule': 'UNRESOLVED_GOTO',
                'goto': goto,
                'msg': f"GOTO 목적지 라벨 '{goto}'이(가) ADDR 선언 목록에 존재하지 않음 [문법 오류]"
            })

        # 4. 행 완전 중복 (ADDR, REMARKS 제외) 검사
        spec_con_key_val_list = []
        for i in range(1, 31):
            spec_con_key_val_list.append(row.get(f'SPEC{i}', '-').strip())
            spec_con_key_val_list.append(row.get(f'CON{i}', '-').strip())
        for i in range(1, 21):
            spec_con_key_val_list.append(row.get(f'KEY{i}', '-').strip())
            spec_con_key_val_list.append(row.get(f'VAL{i}', '-').strip())
        spec_con_key_val_list.append(row.get('GOTO', '-').strip())

        full_tuple = tuple(spec_con_key_val_list)
        is_all_empty = all(x == '-' or x == '' for x in full_tuple)

        if not is_all_empty:
            if full_tuple in seen_full_rows:
                syntax_errors.append({
                    'NO': no,
                    'rule': 'DUPLICATE_FULL_ROW',
                    'first_no': seen_full_rows[full_tuple],
                    'msg': f"행 {no}: ADDR/REMARKS 제외 SPEC+CON+KEY+VAL+GOTO 조합이 행 {seen_full_rows[full_tuple]}와 완벽히 중복됨 [문법 위반]"
                })
            else:
                seen_full_rows[full_tuple] = no

        # 5. SPEC/CON 조건 부분만 중복 검사
        spec_con_tuple = tuple((row.get(f'SPEC{i}', '-').strip(), row.get(f'CON{i}', '-').strip()) for i in range(1, 31))
        is_spec_con_empty = all(s == '-' and c == '-' for s, c in spec_con_tuple)

        if not is_spec_con_empty:
            if spec_con_tuple in seen_spec_con_tuples:
                syntax_errors.append({
                    'NO': no,
                    'rule': 'DUPLICATE_SPEC_CON',
                    'first_no': seen_spec_con_tuples[spec_con_tuple],
                    'msg': f"행 {no}: SPEC/CON 조건 조합이 행 {seen_spec_con_tuples[spec_con_tuple]}와 동일함 [조건 중복]"
                })
            else:
                seen_spec_con_tuples[spec_con_tuple] = no

    # 규칙별 오류 통계 계산
    rule_counts = defaultdict(int)
    for err in syntax_errors:
        rule_counts[err['rule']] += 1

    stats = {
        'total_rows': len(rows),
        'total_errors': len(syntax_errors),
        'total_confirm': len(confirm_needed),
        'rule_counts': dict(rule_counts)
    }

    return syntax_errors, confirm_needed, stats


def generate_report(syntax_errors: list[dict], confirm_needed: list[dict], stats: dict, output_path: Path) -> None:
    """
    검증 결과를 마크다운 형태 보고서 파일로 생성하는 함수.
    
    :param syntax_errors: 문법 오류 목록
    :param confirm_needed: 확인 필요 사항 목록
    :param stats: 통계 데이터
    :param output_path: 저장할 마크다운 파일 경로
    """
    rule_counts = stats['rule_counts']

    lines = []
    lines.append("# PID `EL_PA101A` 로직 문법 및 정합성 검증 보고서")
    lines.append("")
    lines.append("## 1. 검증 개요")
    lines.append(f"- **검증 대상 PID**: `EL_PA101A` (총 {stats['total_rows']}행)")
    lines.append("- **검증 기준 문서**: `logic-syntax.md` (PLM 로직 Editor 문법 규칙) 및 `logic-BOM정합성_작성수정_rule.md`")
    lines.append(f"- **문법 위반/중복 오류 수**: **{stats['total_errors']} 건**")
    lines.append(f"- **확인 필요 사항 수**: **{stats['total_confirm']} 건**")
    lines.append("")

    lines.append("## 2. 규칙별 위반 현황")
    lines.append("| 문법 규칙 항목 | 세부 설명 | 오류/중복 건수 | 판정 |")
    lines.append("|---|---|---:|---|")
    lines.append(f"| **완전 중복행 (`DUPLICATE_FULL_ROW`)** | ADDR/REMARKS 제외 SPEC+CON+KEY+VAL+GOTO 조합 완벽 동일 | {rule_counts.get('DUPLICATE_FULL_ROW', 0)} 건 | {'❌ ERROR' if rule_counts.get('DUPLICATE_FULL_ROW', 0) > 0 else '✅ PASS'} |")
    lines.append(f"| **조건 중복행 (`DUPLICATE_SPEC_CON`)** | SPEC1~30, CON1~30 조건열 조합 완벽 동일 | {rule_counts.get('DUPLICATE_SPEC_CON', 0)} 건 | {'⚠️ WARNING' if rule_counts.get('DUPLICATE_SPEC_CON', 0) > 0 else '✅ PASS'} |")
    lines.append(f"| **KEY / VAL 짝 누락 (`KEY_WITHOUT_VAL`)** | KEY 정의 후 VAL 누락 (또는 반대) | {rule_counts.get('KEY_WITHOUT_VAL', 0)} 건 | {'❌ ERROR' if rule_counts.get('KEY_WITHOUT_VAL', 0) > 0 else '✅ PASS'} |")
    lines.append(f"| **GOTO 라벨 유효성 (`UNRESOLVED_GOTO`)** | GOTO 목적지가 ADDR 선언에 없음 | {rule_counts.get('UNRESOLVED_GOTO', 0)} 건 | {'❌ ERROR' if rule_counts.get('UNRESOLVED_GOTO', 0) > 0 else '✅ PASS'} |")
    lines.append(f"| **SPEC / CON 짝 누락 (`SPEC_MISSING`)** | SPEC 없이 CON만 존재 | {rule_counts.get('SPEC_MISSING', 0)} 건 | {'❌ ERROR' if rule_counts.get('SPEC_MISSING', 0) > 0 else '✅ PASS'} |")
    lines.append(f"| **SPEC 전용 조건 (`SPEC_WITHOUT_CON`)** | SPEC만 있고 CON 공백 | {stats['total_confirm']} 건 | ℹ️ 확인 필요 |")
    lines.append("")

    lines.append("## 3. 세부 위반 및 중복 행 상세 목록")

    if rule_counts.get('DUPLICATE_FULL_ROW', 0) > 0:
        lines.append("### 3.1 완전 중복행 (`DUPLICATE_FULL_ROW`)")
        lines.append("SPEC + CON + KEY + VAL + GOTO 값이 기존 행과 완전히 동일하여 문법에 위반되는 행 목록입니다.")
        for err in syntax_errors:
            if err['rule'] == 'DUPLICATE_FULL_ROW':
                lines.append(f"- **행 {err['NO']}**: 행 {err['first_no']}와 완전 중복")
        lines.append("")

    if rule_counts.get('KEY_WITHOUT_VAL', 0) > 0:
        lines.append("### 3.2 KEY만 선언되고 VAL이 공백인 행 (`KEY_WITHOUT_VAL`)")
        for err in syntax_errors:
            if err['rule'] == 'KEY_WITHOUT_VAL':
                lines.append(f"- **행 {err['NO']}**: KEY='{err['key']}' 만 정의됨")
        lines.append("")

    if rule_counts.get('UNRESOLVED_GOTO', 0) > 0:
        lines.append("### 3.3 미정의 GOTO 라벨 사용 행 (`UNRESOLVED_GOTO`)")
        for err in syntax_errors:
            if err['rule'] == 'UNRESOLVED_GOTO':
                lines.append(f"- **행 {err['NO']}**: GOTO='{err['goto']}' (ADDR에 라벨 없음)")
        lines.append("")

    if rule_counts.get('DUPLICATE_SPEC_CON', 0) > 0:
        lines.append("### 3.4 조건(SPEC/CON) 동일 중복행 (`DUPLICATE_SPEC_CON`)")
        for err in syntax_errors:
            if err['rule'] == 'DUPLICATE_SPEC_CON':
                lines.append(f"- **행 {err['NO']}**: 행 {err['first_no']}와 SPEC/CON 조건 동일")
        lines.append("")

    output_path.write_text('\n'.join(lines), encoding='utf-8')
    print(f"검증 보고서가 성공적으로 생성되었습니다: {output_path}")


def main():
    """
    메인 실행 함수. CSV 데이터를 읽어오고 검증을 실행한 후 결과를 콘솔 및 보고서 파일로 출력.
    """
    project_root = Path(__file__).resolve().parent.parent
    csv_file = project_root / "output_csv" / "EL_PA101A.csv"
    report_file = project_root / "docs" / "EL_PA101A_syntax_report.md"

    if not csv_file.exists():
        print(f"오류: CSV 파일이 존재하지 않습니다. ({csv_file})", file=sys.stderr)
        return 1

    print(f"[{csv_file.name}] 로직 데이터 검증을 시작합니다...")
    rows = load_csv_data(csv_file)
    syntax_errors, confirm_needed, stats = verify_el_pa101a_syntax(rows)

    generate_report(syntax_errors, confirm_needed, stats, report_file)

    # 콘솔 요약 출력
    print("\n==========================================")
    print(f"검증 완료: 총 {stats['total_rows']}행 중 오류 {stats['total_errors']}건, 확인필요 {stats['total_confirm']}건")
    print("==========================================")
    for rule, count in stats['rule_counts'].items():
        print(f" - {rule}: {count}건")

    return 0


if __name__ == "__main__":
    sys.exit(main())
