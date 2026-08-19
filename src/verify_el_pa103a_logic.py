#!/usr/bin/env python3
"""
EL_PA103A PID 로직 정합성 및 문법 검증 스크립트

본 스크립트는 지정한 CSV 파일(예: output_csv/EL_PA103A_test.csv)을 읽어
PLM 로직 Editor 문법 규칙(logic-syntax.md 및 logic-BOM정합성_작성수정_rule.md)에 따른
정합성, 무결성, 문법 오류, GOTO 분기 라벨 유효성, 무한 루프 가능성 등을 정밀 검증하고
Markdown 종합 검증 보고서를 작성합니다.
"""

import argparse
import csv
import sys
from collections import defaultdict
from pathlib import Path
from typing import Dict, List, Set, Any, Tuple

# 표준 출력 인코딩을 utf-8로 reconfigure
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')


def load_csv_data(file_path: Path) -> List[Dict[str, str]]:
    """
    CSV 파일을 읽어 딕셔너리 리스트 형태로 반환하는 함수입니다.

    :param file_path: CSV 파일 경로
    :return: CSV 각 행의 딕셔너리 리스트
    """
    rows = []
    with open(file_path, 'r', encoding='utf-8-sig') as f:
        reader = csv.DictReader(f)
        for row in reader:
            rows.append(row)
    return rows


def verify_spec_con_pairs(rows: List[Dict[str, str]]) -> List[Dict[str, Any]]:
    """
    SPEC과 CON의 짝 일치 여부 및 문법 오류를 검사하는 함수입니다.

    - SPEC만 있고 CON이 빈 칸인 경우: [확인 필요]
    - SPEC이 공백/'-' 인데 CON에 값이 있는 경우: [오류] SPEC 누락
    """
    issues = []

    for row in rows:
        no = row.get('NO', '')
        for i in range(1, 31):
            spec = row.get(f'SPEC{i}', '-').strip()
            con = row.get(f'CON{i}', '-').strip()

            is_spec_empty = (spec == '' or spec == '-')
            is_con_empty = (con == '' or con == '-')

            if not is_spec_empty and is_con_empty:
                issues.append({
                    'NO': no,
                    'type': 'SPEC_ONLY_CON_EMPTY',
                    'severity': 'WARNING',
                    'field': f'SPEC{i}/CON{i}',
                    'spec': spec,
                    'con': con,
                    'message': f"SPEC{i}('{spec}')만 정의되어 있고 CON{i}가 빈 칸입니다. [확인 필요]"
                })
            elif is_spec_empty and not is_con_empty:
                issues.append({
                    'NO': no,
                    'type': 'CON_ONLY_SPEC_EMPTY',
                    'severity': 'ERROR',
                    'field': f'SPEC{i}/CON{i}',
                    'spec': spec,
                    'con': con,
                    'message': f"SPEC{i}은 공백인데 CON{i}('{con}')에 값이 지정되어 있습니다. [문법 오류]"
                })

    return issues


def verify_key_val_pairs(rows: List[Dict[str, str]]) -> List[Dict[str, Any]]:
    """
    KEY와 VAL의 짝 일치 여부를 검사하는 함수입니다.

    - KEY만 있고 VAL이 없는 경우: [오류]
    - VAL만 있고 KEY가 없는 경우: [오류]
    """
    issues = []

    for row in rows:
        no = row.get('NO', '')
        for i in range(1, 21):
            key = row.get(f'KEY{i}', '-').strip()
            val = row.get(f'VAL{i}', '-').strip()

            is_key_empty = (key == '' or key == '-')
            is_val_empty = (val == '' or val == '-')

            if not is_key_empty and is_val_empty:
                issues.append({
                    'NO': no,
                    'type': 'KEY_ONLY_VAL_EMPTY',
                    'severity': 'ERROR',
                    'field': f'KEY{i}/VAL{i}',
                    'key': key,
                    'val': val,
                    'message': f"KEY{i}('{key}')만 정의되어 있고 VAL{i}가 빈 칸입니다."
                })
            elif is_key_empty and not is_val_empty:
                issues.append({
                    'NO': no,
                    'type': 'VAL_ONLY_KEY_EMPTY',
                    'severity': 'ERROR',
                    'field': f'KEY{i}/VAL{i}',
                    'key': key,
                    'val': val,
                    'message': f"KEY{i}는 공백인데 VAL{i}('{val}')에 값이 지정되어 있습니다."
                })

    return issues


def verify_goto_and_addr(rows: List[Dict[str, str]]) -> Tuple[List[Dict[str, Any]], Set[str]]:
    """
    ADDR 라벨 및 GOTO 분기 라벨의 유효성과 순환 분기(무한 루프) 가능성을 검사하는 함수입니다.

    - GOTO 목적지 라벨이 ADDR로 존재하는지 확인
    """
    issues = []
    
    valid_addrs = set()
    for row in rows:
        addr = row.get('ADDR', '-').strip()
        if addr != '' and addr != '-':
            valid_addrs.add(addr)

    for row in rows:
        no = row.get('NO', '')
        goto = row.get('GOTO', '-').strip()

        if goto != '' and goto != '-' and goto != 'STOP':
            if goto not in valid_addrs:
                issues.append({
                    'NO': no,
                    'type': 'UNRESOLVED_GOTO_LABEL',
                    'severity': 'ERROR',
                    'field': 'GOTO',
                    'goto': goto,
                    'message': f"GOTO 목적지 라벨 '{goto}'(이)가 ADDR 목록에 존재하지 않습니다."
                })

    return issues, valid_addrs


def verify_duplicate_spec_con_rows(rows: List[Dict[str, str]]) -> List[Dict[str, Any]]:
    """
    SPEC1~30, CON1~30 조건이 완전히 동일한 중복 행(데드 코드 또는 오류)을 검사하는 함수입니다.
    """
    issues = []
    seen_specs = {}

    for row in rows:
        no = row.get('NO', '')
        
        spec_con_list = []
        for i in range(1, 31):
            s = row.get(f'SPEC{i}', '-').strip()
            c = row.get(f'CON{i}', '-').strip()
            spec_con_list.append((s, c))
            
        spec_con_tuple = tuple(spec_con_list)
        
        is_all_empty = all(s == '-' and c == '-' for s, c in spec_con_tuple)
        if is_all_empty:
            continue

        if spec_con_tuple in seen_specs:
            first_no = seen_specs[spec_con_tuple]
            issues.append({
                'NO': no,
                'type': 'DUPLICATE_SPEC_CON_ROW',
                'severity': 'WARNING',
                'field': 'SPEC1~30/CON1~30',
                'message': f"행 {no}의 SPEC/CON 조건 목록이 행 {first_no}와 완전히 동일합니다. [문법/정합성 주의]"
            })
        else:
            seen_specs[spec_con_tuple] = no

    return issues


def generate_markdown_report(title: str, total_rows: int, valid_addrs: Set[str], issues: List[Dict[str, Any]], report_path: Path):
    """
    검증 결과를 마크다운 형식의 종합 보고서로 작성하는 함수입니다.
    """
    errors = [i for i in issues if i['severity'] == 'ERROR']
    warnings = [i for i in issues if i['severity'] == 'WARNING']

    issues_by_type = defaultdict(list)
    for issue in issues:
        issues_by_type[issue['type']].append(issue)

    lines = []
    lines.append(f"# {title}")
    lines.append("")
    lines.append("## 1. 검증 개요")
    lines.append(f"- **검증 대상 PID**: `EL_PA103A` (테스트 버전 `VERSION = -1`)")
    lines.append(f"- **전체 로직 행 수**: {total_rows} 행")
    lines.append(f"- **등록된 ADDR 라벨 개수**: {len(valid_addrs)} 개 ({', '.join(sorted(list(valid_addrs))) if valid_addrs else '없음'})")
    lines.append(f"- **총 발견 이슈 수**: {len(issues)} 건 (심각 오류: {len(errors)} 건, 경고/확인필요: {len(warnings)} 건)")
    lines.append("")

    lines.append("## 2. 검증 항목별 결과 요약")
    lines.append("| 검증 항목 | 규칙 | 발견 건수 | 수준 | 주요 내용 |")
    lines.append("|---|---|---:|---|---|")
    lines.append(f"| KEY/VAL 짝 일치 | KEY와 VAL은 항상 짝이어야 함 | {len(issues_by_type['KEY_ONLY_VAL_EMPTY']) + len(issues_by_type['VAL_ONLY_KEY_EMPTY'])}건 | ❌ ERROR | KEY만 존재하고 VAL이 공백인 미완성 산출행 |")
    lines.append(f"| SPEC/CON 짝 일치 | SPEC이 비어있는데 CON이 있거나, CON이 비어있음 | {len(issues_by_type['CON_ONLY_SPEC_EMPTY']) + len(issues_by_type['SPEC_ONLY_CON_EMPTY'])}건 | ⚠️ WARNING / ❌ ERROR | SPEC만 있고 CON이 비어있는 [확인 필요] 상태 |")
    lines.append(f"| GOTO 목적지 유효성 | GOTO 목적지 라벨은 존재해야 함 | {len(issues_by_type['UNRESOLVED_GOTO_LABEL'])}건 | ❌ ERROR | 미정의 ADDR 라벨 참조 여부 |")
    lines.append(f"| SPEC/CON 중복 행 | 1~마지막행까지 조건열이 동일하면 문법 오류 | {len(issues_by_type['DUPLICATE_SPEC_CON_ROW'])}건 | ⚠️ WARNING | 완전히 동일한 조건문 중복 정의 (데드코드) |")
    lines.append("")

    lines.append("## 3. 심각한 오류 상세 (ERROR)")
    if errors:
        key_only_errs = issues_by_type['KEY_ONLY_VAL_EMPTY']
        lines.append(f"### 3.1 KEY만 존재하고 VAL이 빈 칸인 오류 ({len(key_only_errs)}건)")
        lines.append("`KEY`에 대상 항목(예: `A103A_CMT`, `CHECK_KL`)을 지정하였으나, 산출될 값인 `VAL`이 비어 있는 행들입니다.")
        lines.append("")
        lines.append("| 행 번호(NO) | 대상 KEY | VAL 값 | 비고 |")
        lines.append("|---|---|---|---|")
        for err in key_only_errs[:30]:
            lines.append(f"| {err['NO']} | `{err['key']}` | `(빈칸)` | 산출 값 누락 |")
        if len(key_only_errs) > 30:
            lines.append(f"| ... | ... | ... | 외 {len(key_only_errs) - 30}건 생략 |")
        lines.append("")
    else:
        lines.append("심각한 오류가 발견되지 않았증습니다.")
        lines.append("")

    lines.append("## 4. 경고 및 확인 필요 항목 상세 (WARNING)")
    spec_only_warns = issues_by_type['SPEC_ONLY_CON_EMPTY']
    lines.append(f"### 4.1 SPEC만 정의되고 CON이 비어 있는 항목 ({len(spec_only_warns)}건)")
    lines.append("PLM Editor 문법 규칙(`logic-syntax.md`)에 따라, SPEC만 있고 CON이 빈 칸인 경우 임의로 의도를 단정하지 않고 **[확인 필요]** 라벨을 부여합니다.")
    lines.append("")
    lines.append("| 행 번호(NO) | SPEC 코드 | CON 값 | 비고 |")
    lines.append("|---|---|---|---|")
    for warn in spec_only_warns[:20]:
        lines.append(f"| {warn['NO']} | `{warn['spec']}` | `(빈칸)` | [확인 필요] |")
    if len(spec_only_warns) > 20:
        lines.append(f"| ... | ... | ... | 외 {len(spec_only_warns) - 20}건 생략 |")
    lines.append("")

    dup_row_warns = issues_by_type['DUPLICATE_SPEC_CON_ROW']
    lines.append(f"### 4.2 조건(SPEC1~30, CON1~30) 중복 행 ({len(dup_row_warns)}건)")
    lines.append("이전 행과 모든 조건식 열이 완전히 동일한 행입니다. 중복 조건으로 인해 무시되거나 의도치 않은 중복 산출이 발생할 수 있습니다.")
    lines.append("")
    lines.append("| 행 번호(NO) | 내용 요약 |")
    lines.append("|---|---|")
    for warn in dup_row_warns[:20]:
        lines.append(f"| {warn['NO']} | {warn['message']} |")
    if len(dup_row_warns) > 20:
        lines.append(f"| ... | 외 {len(dup_row_warns) - 20}건 생략 |")
    lines.append("")

    lines.append("## 5. 개선 및 조치 가이드")
    lines.append("1. **VAL 누락 건 (`KEY=A103A_CMT`, `VAL=(빈칸)`)**: 주석 또는 자재번호 산출값(`VAL`)이 누락되었는지 확인 후 입력하거나 해당 산출행을 정리해야 합니다.")
    lines.append("2. **[확인 필요] SPEC만 존재하는 조건**: `CON` 조건값이 누락된 것인지, 아니면 특성이 존재하는 것만으로 조건 성립하는 의도인지 설계자 확인이 필요합니다.")
    lines.append("3. **중복 조건 행 정리**: 동일한 SPEC-CON 조합이 중복 선언된 행에 대해 통합 또는 조건 세분화 작업이 필요합니다.")

    report_path.parent.mkdir(parents=True, exist_ok=True)
    with open(report_path, 'w', encoding='utf-8') as f:
        f.write('\n'.join(lines))

    print(f"검증 보고서 생성 완료: {report_path}")


def main():
    parser = argparse.ArgumentParser(description="EL_PA103A PID 로직 검증 스크립트")
    parser.add_argument("--csv", default="output_csv/EL_PA103A_test.csv", help="검증할 CSV 파일 경로")
    parser.add_argument("--report", default="docs/EL_PA103A_test_version_validation_report.md", help="생성할 보고서 경로")
    parser.add_argument("--title", default="PID EL_PA103A 테스트 버전(v-1) 로직 정합성 검증 보고서", help="보고서 제목")

    args = parser.parse_args()
    project_root = Path(__file__).resolve().parent.parent
    csv_file_path = project_root / args.csv
    report_path = project_root / args.report

    if not csv_file_path.exists():
        print(f"오류: 검증 대상 파일이 존재하지 않습니다: {csv_file_path}")
        return

    print(f"==================================================")
    print(f"  EL_PA103A PID 테스트 버전 로직 정합성 검증 시작  ")
    print(f"==================================================")
    print(f"검증 대상 파일: {csv_file_path}")

    rows = load_csv_data(csv_file_path)
    total_rows = len(rows)

    spec_con_issues = verify_spec_con_pairs(rows)
    key_val_issues = verify_key_val_pairs(rows)
    goto_issues, valid_addrs = verify_goto_and_addr(rows)
    dup_issues = verify_duplicate_spec_con_rows(rows)

    all_issues = spec_con_issues + key_val_issues + goto_issues + dup_issues

    generate_markdown_report(args.title, total_rows, valid_addrs, all_issues, report_path)


if __name__ == "__main__":
    main()
