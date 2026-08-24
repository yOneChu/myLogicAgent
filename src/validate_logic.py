#!/usr/bin/env python3
"""
PLM 로직 데이터 정합성 검증 스크립트 (EL_PA115A02 등)

검증 규칙:
1. SPEC이 빈 값(공백)인데 CON에 값이 있는 경우 -> [오류] SPEC 없이 CON만 존재
2. SPEC에 값이 있으나 CON이 빈 값인 경우 -> [확인 필요] SPEC만 존재하고 CON은 공백
3. ADDR, REMARKS를 제외한 (SPEC 1~30, CON 1~30, KEY 1~20, VAL 1~20, GOTO) 전체 조합의 완전 중복 행 -> [오류] 중복 행 존재
4. ADDR, REMARKS 제외 SPEC 1~30, CON 1~30 조건 조합이 동일한 중복 그룹 분석
5. KEY는 있으나 VAL이 없는 경우 또는 VAL은 있으나 KEY가 없는 경우 -> [오류/경고] KEY-VAL 불일치
"""

import csv
import json
import sys
from collections import defaultdict
from typing import Dict, List, Tuple, Any

def load_csv_data(csv_path: str) -> List[Dict[str, str]]:
    """
    CSV 파일에서 로직 데이터를 읽어와 리스트(dict) 형태로 반환합니다.
    
    :param csv_path: 읽어올 CSV 파일 경로
    :return: 로직 행별 Dictionary 목록
    """
    rows = []
    with open(csv_path, "r", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        for row in reader:
            rows.append(row)
    return rows


def validate_spec_con_pairs(rows: List[Dict[str, str]]) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
    """
    각 행의 SPEC/CON 짝 설정 규칙을 검증합니다.
    - SPEC은 없는데 CON만 존재하는 경우 (오류)
    - SPEC만 있고 CON은 공백인 경우 (확인 필요)
    
    :param rows: CSV 로직 행 데이터 리스트
    :return: (errors, warnings) 검증 결과 리스트 튜플
    """
    errors = []
    warnings = []

    for row in rows:
        no = row.get("NO", "")
        addr = row.get("ADDR", "").strip()
        remarks = row.get("REMARKS", "").strip()

        for i in range(1, 31):
            spec = row.get(f"SPEC{i}", "").strip() if row.get(f"SPEC{i}") else ""
            con = row.get(f"CON{i}", "").strip() if row.get(f"CON{i}") else ""

            # 1. SPEC이 공백인데 CON에 값이 존재하면 오류
            if not spec and con:
                errors.append({
                    "NO": no,
                    "ADDR": addr,
                    "PAIR_INDEX": i,
                    "SPEC": spec,
                    "CON": con,
                    "REASON": f"SPEC{i}이(가) 빈 값인데 CON{i}='{con}' 값이 존재함 (문법 오류)"
                })

            # 2. SPEC은 존재하지만 CON이 빈 값인 경우 [확인 필요]
            elif spec and not con:
                warnings.append({
                    "NO": no,
                    "ADDR": addr,
                    "PAIR_INDEX": i,
                    "SPEC": spec,
                    "CON": con,
                    "REASON": f"SPEC{i}='{spec}'만 존재하고 CON{i}이(가) 빈 값임 ([확인 필요])"
                })

    return errors, warnings


def validate_key_val_pairs(rows: List[Dict[str, str]]) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
    """
    각 행의 KEY/VAL 짝 설정 규칙을 검증합니다.
    - KEY가 없는데 VAL만 있는 경우
    - KEY는 있으나 VAL이 없는 경우
    
    :param rows: CSV 로직 행 데이터 리스트
    :return: (errors, warnings) 검증 결과 리스트 튜플
    """
    errors = []
    warnings = []

    for row in rows:
        no = row.get("NO", "")
        addr = row.get("ADDR", "").strip()

        for i in range(1, 21):
            key = row.get(f"KEY{i}", "").strip() if row.get(f"KEY{i}") else ""
            val = row.get(f"VAL{i}", "").strip() if row.get(f"VAL{i}") else ""

            if not key and val:
                errors.append({
                    "NO": no,
                    "ADDR": addr,
                    "PAIR_INDEX": i,
                    "KEY": key,
                    "VAL": val,
                    "REASON": f"KEY{i}이(가) 빈 값인데 VAL{i}='{val}' 값이 존재함 (문법 오류)"
                })
            elif key and not val:
                warnings.append({
                    "NO": no,
                    "ADDR": addr,
                    "PAIR_INDEX": i,
                    "KEY": key,
                    "VAL": val,
                    "REASON": f"KEY{i}='{key}'만 존재하고 VAL{i}이(가) 빈 값임 ([확인 필요])"
                })

    return errors, warnings


def check_full_duplicates(rows: List[Dict[str, str]]) -> List[Dict[str, Any]]:
    """
    ADDR과 REMARKS를 제외하고 SPEC, CON, KEY, VAL, GOTO 필드 조합이 완전히 일치하는 중복 행을 검출합니다.
    
    :param rows: CSV 로직 행 데이터 리스트
    :return: 중복 행 그룹 리스트
    """
    combo_map = defaultdict(list)

    for row in rows:
        no = row.get("NO", "")
        addr = row.get("ADDR", "").strip()
        remarks = row.get("REMARKS", "").strip()
        goto_val = row.get("GOTO", "").strip() if row.get("GOTO") else ""

        key_tuple = [("GOTO", goto_val)]
        for i in range(1, 31):
            s = row.get(f"SPEC{i}", "").strip() if row.get(f"SPEC{i}") else ""
            c = row.get(f"CON{i}", "").strip() if row.get(f"CON{i}") else ""
            key_tuple.append((f"SPEC{i}", s))
            key_tuple.append((f"CON{i}", c))

        for i in range(1, 21):
            k = row.get(f"KEY{i}", "").strip() if row.get(f"KEY{i}") else ""
            v = row.get(f"VAL{i}", "").strip() if row.get(f"VAL{i}") else ""
            key_tuple.append((f"KEY{i}", k))
            key_tuple.append((f"VAL{i}", v))

        combo_key = tuple(key_tuple)
        combo_map[combo_key].append({"NO": no, "ADDR": addr, "REMARKS": remarks})

    duplicates = []
    for combo, line_list in combo_map.items():
        if len(line_list) > 1:
            # 빈 행 여부 체크
            non_empty_items = [(k, v) for k, v in combo if v != ""]
            duplicates.append({
                "lines": [item["NO"] for item in line_list],
                "line_count": len(line_list),
                "is_empty_line": len(non_empty_items) == 0,
                "details": line_list,
                "non_empty_fields": non_empty_items
            })

    return duplicates


def check_spec_con_duplicates(rows: List[Dict[str, str]]) -> List[Dict[str, Any]]:
    """
    ADDR과 REMARKS를 제외하고 SPEC1~30, CON1~30 조건만 일치하는 행 그룹을 검출합니다.
    
    :param rows: CSV 로직 행 데이터 리스트
    :return: SPEC+CON 조건 중복 그룹 리스트
    """
    combo_map = defaultdict(list)

    for row in rows:
        no = row.get("NO", "")
        addr = row.get("ADDR", "").strip()
        remarks = row.get("REMARKS", "").strip()

        key_tuple = []
        for i in range(1, 31):
            s = row.get(f"SPEC{i}", "").strip() if row.get(f"SPEC{i}") else ""
            c = row.get(f"CON{i}", "").strip() if row.get(f"CON{i}") else ""
            key_tuple.append((f"SPEC{i}", s))
            key_tuple.append((f"CON{i}", c))

        combo_key = tuple(key_tuple)
        combo_map[combo_key].append({"NO": no, "ADDR": addr, "REMARKS": remarks})

    spec_con_dups = []
    for combo, line_list in combo_map.items():
        if len(line_list) > 1:
            non_empty_items = [(k, v) for k, v in combo if v != ""]
            spec_con_dups.append({
                "lines": [item["NO"] for item in line_list],
                "line_count": len(line_list),
                "is_empty_cond": len(non_empty_items) == 0,
                "details": line_list,
                "spec_con_pairs": non_empty_items
            })

    return spec_con_dups


def run_full_validation(csv_path: str, pid_name: str = "EL_PA115A02") -> Dict[str, Any]:
    """
    전체 로직 검증 프로세스를 수행하고 검증 리포트를 생성합니다.
    
    :param csv_path: 로직 데이터 CSV 파일 경로
    :param pid_name: PID명 (기본값: EL_PA115A02)
    :return: 종합 검증 결과 사전 객체
    """
    rows = load_csv_data(csv_path)
    total_rows = len(rows)

    spec_con_errors, spec_con_warnings = validate_spec_con_pairs(rows)
    key_val_errors, key_val_warnings = validate_key_val_pairs(rows)
    full_duplicates = check_full_duplicates(rows)
    spec_con_duplicates = check_spec_con_duplicates(rows)

    report = {
        "PID": pid_name,
        "total_rows": total_rows,
        "spec_con_errors": spec_con_errors,
        "spec_con_warnings": spec_con_warnings,
        "key_val_errors": key_val_errors,
        "key_val_warnings": key_val_warnings,
        "full_duplicates": full_duplicates,
        "spec_con_duplicates": spec_con_duplicates,
    }

    return report


def main():
    csv_path = "output_csv/el_pa115a02.csv"
    if len(sys.argv) > 1:
        csv_path = sys.argv[1]

    print(f"=== {csv_path} 로직 정합성 검증 시작 ===")
    report = run_full_validation(csv_path, pid_name="EL_PA115A02")

    print(f"총 행 수: {report['total_rows']}개")
    print(f"1. SPEC/CON 문법 오류 건수: {len(report['spec_con_errors'])}건")
    print(f"2. SPEC만 존재하는 [확인 필요] 건수: {len(report['spec_con_warnings'])}건")
    print(f"3. KEY/VAL 문법 오류 건수: {len(report['key_val_errors'])}건")
    print(f"4. KEY만 존재하는 [확인 필요] 건수: {len(report['key_val_warnings'])}건")
    print(f"5. 전체 (SPEC+CON+KEY+VAL+GOTO) 완전 중복 그룹: {len(report['full_duplicates'])}개")
    print(f"6. SPEC+CON 조건 중복 그룹: {len(report['spec_con_duplicates'])}개")

    print("\n--- [상세 결과] ---")

    if report['spec_con_errors']:
        print("\n[오류] SPEC 공백, CON 존재:")
        for err in report['spec_con_errors']:
            print(f"  - 라인 {err['NO']} (ADDR: '{err['ADDR']}'): {err['REASON']}")

    if report['spec_con_warnings']:
        print("\n[확인 필요] SPEC 존재, CON 공백:")
        for warn in report['spec_con_warnings']:
            print(f"  - 라인 {warn['NO']} (ADDR: '{warn['ADDR']}'): {warn['REASON']}")

    if report['key_val_errors']:
        print("\n[오류] KEY 공백, VAL 존재:")
        for err in report['key_val_errors']:
            print(f"  - 라인 {err['NO']} (ADDR: '{err['ADDR']}'): {err['REASON']}")

    if report['key_val_warnings']:
        print("\n[확인 필요] KEY 존재, VAL 공백:")
        for warn in report['key_val_warnings']:
            print(f"  - 라인 {warn['NO']} (ADDR: '{warn['ADDR']}'): {warn['REASON']}")

    if report['full_duplicates']:
        print("\n[오류] 완전 동일 중복 행 그룹 (문법 어긋남):")
        for idx, dup in enumerate(report['full_duplicates'], 1):
            lines_str = ", ".join(dup['lines'])
            if dup['is_empty_line']:
                print(f"  - 그룹 {idx} (라인: {lines_str}): 완전 빈 행 중복")
            else:
                print(f"  - 그룹 {idx} (라인: {lines_str}): {dup['line_count']}개 행 완전 동일")
                print(f"    필드: {dup['non_empty_fields']}")

    if report['spec_con_duplicates']:
        print("\n[참고/분석] SPEC+CON 조건 동일 그룹:")
        for idx, dup in enumerate(report['spec_con_duplicates'], 1):
            lines_str = ", ".join(dup['lines'])
            if dup['is_empty_cond']:
                print(f"  - 조건 없음 (라인: {lines_str}): 조건 없는 행 {dup['line_count']}개")
            else:
                pairs_str = ", ".join([f"{k}={v}" for k, v in dup['spec_con_pairs']])
                print(f"  - 그룹 {idx} (라인: {lines_str}): {dup['line_count']}개 행 조건 동일 [{pairs_str}]")

if __name__ == "__main__":
    main()
