#!/usr/bin/env python3
"""
PID EL_PA103A 테스트 버전의 SPEC 및 CON 특성값과
reference/엘리베이터_특성코드.csv 마스터 데이터 간 전수 대조 검증 스크립트
"""

import csv
import re
import sys
from collections import defaultdict
from pathlib import Path

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')


def load_master_data(master_csv_path: Path):
    """
    reference/엘리베이터_특성코드.csv 파일에서
    특성코드(code) 및 특성값(typeVal) 세트를 추출하는 함수입니다.
    """
    valid_codes = set()
    code_to_vals = defaultdict(set)

    with open(master_csv_path, 'r', encoding='utf-8-sig') as f:
        reader = csv.DictReader(f)
        for row in reader:
            code = row.get('code', '').strip()
            type_val = row.get('typeVal', '').strip()

            if code:
                valid_codes.add(code)
                if type_val:
                    code_to_vals[code].add(type_val)

    return valid_codes, code_to_vals


def parse_con_values(con_str: str) -> list[str]:
    """
    CON 문법 표기법(단일값, 목록, 부정!, 와일드카드?)을 고려하여
    개별 검증용 특성값 리스트를 분리하는 함수입니다.
    """
    val = con_str.strip()
    if not val or val == '-':
        return []

    # 부정 ! 제거
    if val.startswith('!'):
        val = val[1:]

    # 비교식 (예: >=550,<=1250) 은 수치 범위이므로 제외
    if re.search(r'(>=|<=|>|<|=)\s*[\d\.\-]+', val):
        return []

    # 목록 표기법 (,val1,val2,)
    if ',' in val:
        tokens = [t.strip() for t in val.split(',') if t.strip()]
        return tokens

    # 와일드카드 ? 가 포함된 경우 검증에서 제외
    if '?' in val:
        return []

    return [val]


def verify_el_pa103a_against_master():
    project_root = Path(__file__).resolve().parent.parent
    master_csv = project_root / "reference" / "엘리베이터_특성코드.csv"
    test_csv = project_root / "output_csv" / "EL_PA103A_test.csv"

    valid_codes, code_to_vals = load_master_data(master_csv)

    with open(test_csv, 'r', encoding='utf-8-sig') as f:
        rows = list(csv.DictReader(f))

    print(f"=== PID EL_PA103A 테스트 버전 사양 마스터 데이터 대조 검증 ===")
    print(f"마스터 특성코드 개수: {len(valid_codes)} 개")
    print(f"검증 대상 데이터: {test_csv} (총 {len(rows)} 행)\n")

    unregistered_specs = defaultdict(list)
    unregistered_cons = defaultdict(list)
    valid_spec_con_count = 0

    for r in rows:
        no = r.get('NO', '')

        for i in range(1, 31):
            s = r.get(f'SPEC{i}', '-').strip()
            c = r.get(f'CON{i}', '-').strip()

            if not s or s == '-':
                continue

            # 1. SPEC 코드 마스터 등록 여부
            if s not in valid_codes:
                unregistered_specs[s].append(no)
            else:
                # 2. CON 특성값 마스터 등록 여부
                if c and c != '-':
                    con_vals = parse_con_values(c)
                    master_vals = code_to_vals.get(s, set())

                    for cv in con_vals:
                        # KEY-IN 특성 (마스터 값 리스트가 비어 있거나 KEY-IN 특성) 인 경우 제외
                        if master_vals and cv not in master_vals:
                            unregistered_cons[(s, cv)].append((no, c))
                        else:
                            valid_spec_con_count += 1

    print("--- 1. 미등록 특성코드 (SPEC) 검증 결과 ---")
    if unregistered_specs:
        print(f"❌ 마스터 데이터 미등록 SPEC 코드 발견: {len(unregistered_specs)} 개")
        for s, nos in unregistered_specs.items():
            no_str = ", ".join(nos[:10]) + ("..." if len(nos) > 10 else "")
            print(f"  - SPEC '{s}': {len(nos)}회 등장 (NO {no_str})")
    else:
        print("✅ 사용된 모든 SPEC 특성코드가 마스터 데이터에 정상 등록되어 있습니다!")
    print()

    print("--- 2. 미등록 / 오류 특성값 (CON) 검증 결과 ---")
    if unregistered_cons:
        print(f"❌ 마스터 데이터 미등록 / 불일치 CON 값 발견: {len(unregistered_cons)} 건")
        for (s, cv), examples in list(unregistered_cons.items())[:20]:
            ex_str = ", ".join([f"NO {e[0]} ('{e[1]}')" for e in examples[:3]])
            print(f"  - SPEC '{s}' 의 CON 값 '{cv}': 마스터 미등록 (발생 건수 {len(examples)}건, 예: {ex_str})")
        if len(unregistered_cons) > 20:
            print(f"  ... 외 {len(unregistered_cons) - 20}건 생략")
    else:
        print("✅ 사용된 모든 CON 특성값이 마스터 데이터와 100% 일치합니다!")
    print()

    # 결과 마크다운 보고서 저장
    report_lines = []
    report_lines.append("# PID `EL_PA103A` 테스트 버전 SPEC/CON 사양 마스터 데이터 대조 검증 보고서")
    report_lines.append("")
    report_lines.append("## 1. 검증 개요")
    report_lines.append(f"- **검증 대상 PID**: `EL_PA103A` (테스트 버전 `VERSION = -1`, 총 {len(rows)}행)")
    report_lines.append(f"- **기준 마스터 데이터**: [엘리베이터_특성코드.csv](file:///{master_csv.as_posix()}) (총 {len(valid_codes)}개 특성코드)")
    report_lines.append(f"- **미등록 SPEC 코드 수**: **{len(unregistered_specs)} 개**")
    report_lines.append(f"- **미등록/오류 CON 특성값 수**: **{len(unregistered_cons)} 건**")
    report_lines.append("")

    report_lines.append("## 2. 미등록 특성코드 (SPEC) 상세")
    if unregistered_specs:
        report_lines.append("| 특성코드 (SPEC) | 검증 결과 | 등장 횟수 | 발생 행 번호 (NO) 예시 |")
        report_lines.append("|---|---|---:|---|")
        for s, nos in unregistered_specs.items():
            no_str = ", ".join(nos[:8]) + ("..." if len(nos) > 8 else "")
            report_lines.append(f"| `{s}` | ❌ 마스터 미등록 | {len(nos)}회 | NO {no_str} |")
    else:
        report_lines.append("사용된 모든 SPEC 특성코드가 마스터 데이터베이스에 정식 등록되어 있습니다.")
    report_lines.append("")

    report_lines.append("## 3. 미등록 및 불일치 특성값 (CON) 상세")
    if unregistered_cons:
        report_lines.append("| 특성코드 (SPEC) | 입력된 CON 값 | 검증 결과 | 발생 건수 | 대표 행 번호 (NO) |")
        report_lines.append("|---|---|---|---:|---|")
        for (s, cv), examples in list(unregistered_cons.items()):
            ex_str = ", ".join([f"NO {e[0]}" for e in examples[:5]])
            report_lines.append(f"| `{s}` | `{cv}` | ❌ 마스터 미등록 값 | {len(examples)}건 | {ex_str} |")
    else:
        report_lines.append("검증된 모든 CON 특성값이 마스터 사양 데이터와 100% 정상 일치합니다.")
    report_lines.append("")

    report_lines.append("## 4. 조치 권장사항")
    if unregistered_specs or unregistered_cons:
        report_lines.append("1. 마스터 미등록 SPEC/CON 값은 수배 엔진 실행 시 사양 일치 실패(Mismatch)를 유발하므로 마스터 등록 여부 재확인 또는 로직 수정이 필요합니다.")
    else:
        report_lines.append("모든 특성코드 및 특성값이 사양 마스터 데이터와 완벽히 일치하므로 수배 실행 시 사양 일치 오류가 발생하지 않습니다.")

    report_path = test_csv.parent.parent / "docs" / "EL_PA103A_master_spec_con_validation_report.md"
    report_path.write_text('\n'.join(report_lines), encoding='utf-8')
    print(f"마스터 대조 검증 보고서 생성 완료: {report_path}")


if __name__ == "__main__":
    verify_el_pa103a_against_master()
