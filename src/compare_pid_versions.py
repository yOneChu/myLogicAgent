#!/usr/bin/env python3
"""
PID 버전 간 비교 분석 자동화 스크립트입니다.
지정한 PID 및 두 개의 버전(또는 최신/직전 버전)을 비교하여 CSV, Excel 및 분석 보고서를 자동으로 생성합니다.

사용 예시:
  uv run python src/compare_pid_versions.py --pid B181A01 --v1 28 --v2 29
  uv run python src/compare_pid_versions.py --pid B181A01 (최신 2개 버전 자동 비교)
"""

import argparse
import csv
import subprocess
import sys
from pathlib import Path
from typing import Dict, List, Any, Tuple

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

# 프로젝트 루트 디렉터리 경로 설정
ROOT_DIR = Path(__file__).resolve().parent.parent
CSV_DIR = ROOT_DIR / "output_csv"
EXCEL_DIR = ROOT_DIR / "output_excel"
DOCS_DIR = ROOT_DIR / "docs"
SCRIPTS_DIR = ROOT_DIR / "scripts" / "db_query"


def fetch_pid_versions(pid: str) -> List[Dict[str, str]]:
    """
    DB에서 해당 PID의 전체 버전 및 HOUID 목록을 조회하여 리스트로 반환하는 함수입니다.
    
    :param pid: PID명 (예: B181A01)
    :return: 버전 정보 딕셔너리 리스트
    """
    sql = f"SELECT PID, VERSION, HOUID, REG_DATE FROM HDEL_DEFAULT.VARIANT_H WHERE PID = '{pid}' ORDER BY TO_NUMBER(CASE WHEN VERSION = '-1' THEN '999999' ELSE VERSION END)"
    temp_csv = CSV_DIR / f"{pid}_version_list.csv"
    
    cmd = [
        sys.executable,
        str(SCRIPTS_DIR / "query_to_csv.py"),
        "--sql", sql,
        "--output", str(temp_csv)
    ]
    
    result = subprocess.run(cmd, capture_output=True, text=True, encoding='utf-8', errors='replace')
    if result.returncode != 0:
        raise RuntimeError(f"버전 목록 조회 실패: {result.stderr}")
        
    versions = []
    if temp_csv.exists():
        with open(temp_csv, 'r', encoding='utf-8-sig') as f:
            reader = csv.DictReader(f)
            for row in reader:
                # 테스트 버전(-1) 제외하고 정수 버전만 수집
                ver = row.get('VERSION', '').strip()
                if ver != '-1':
                    versions.append(row)
                    
    return versions


def run_comparison_queries(pid: str, v1: str, v2: str) -> Tuple[Path, Path]:
    """
    지정된 PID 및 두 버전에 대한 데이터베이스 쿼리를 실행하여 CSV 및 Excel 파일로 저장하는 함수입니다.
    
    :param pid: PID명
    :param v1: 첫 번째 비교 버전
    :param v2: 두 번째 비교 버전
    :return: (csv_path, excel_path) 튜플
    """
    sql = f"""SELECT H.PID,
       H.VERSION,
       D.HOUID,
       D.NO,
       NVL(D.ADDR, '-') AS ADDR,
       NVL(D.GOTO, '-') AS GOTO,
       NVL(D.REMARKS, '-') AS REMARKS,
       NVL(D.SPEC1, '-') AS SPEC1, NVL(D.CON1, '-') AS CON1,
       NVL(D.SPEC2, '-') AS SPEC2, NVL(D.CON2, '-') AS CON2,
       NVL(D.SPEC3, '-') AS SPEC3, NVL(D.CON3, '-') AS CON3,
       NVL(D.SPEC4, '-') AS SPEC4, NVL(D.CON4, '-') AS CON4,
       NVL(D.SPEC5, '-') AS SPEC5, NVL(D.CON5, '-') AS CON5,
       NVL(D.SPEC6, '-') AS SPEC6, NVL(D.CON6, '-') AS CON6,
       NVL(D.SPEC7, '-') AS SPEC7, NVL(D.CON7, '-') AS CON7,
       NVL(D.SPEC8, '-') AS SPEC8, NVL(D.CON8, '-') AS CON8,
       NVL(D.SPEC9, '-') AS SPEC9, NVL(D.CON9, '-') AS CON9,
       NVL(D.SPEC10, '-') AS SPEC10, NVL(D.CON10, '-') AS CON10,
       NVL(D.SPEC11, '-') AS SPEC11, NVL(D.CON11, '-') AS CON11,
       NVL(D.SPEC12, '-') AS SPEC12, NVL(D.CON12, '-') AS CON12,
       NVL(D.SPEC13, '-') AS SPEC13, NVL(D.CON13, '-') AS CON13,
       NVL(D.SPEC14, '-') AS SPEC14, NVL(D.CON14, '-') AS CON14,
       NVL(D.SPEC15, '-') AS SPEC15, NVL(D.CON15, '-') AS CON15,
       NVL(D.SPEC16, '-') AS SPEC16, NVL(D.CON16, '-') AS CON16,
       NVL(D.SPEC17, '-') AS SPEC17, NVL(D.CON17, '-') AS CON17,
       NVL(D.SPEC18, '-') AS SPEC18, NVL(D.CON18, '-') AS CON18,
       NVL(D.SPEC19, '-') AS SPEC19, NVL(D.CON19, '-') AS CON19,
       NVL(D.SPEC20, '-') AS SPEC20, NVL(D.CON20, '-') AS CON20,
       NVL(D.SPEC21, '-') AS SPEC21, NVL(D.CON21, '-') AS CON21,
       NVL(D.SPEC22, '-') AS SPEC22, NVL(D.CON22, '-') AS CON22,
       NVL(D.SPEC23, '-') AS SPEC23, NVL(D.CON23, '-') AS CON23,
       NVL(D.SPEC24, '-') AS SPEC24, NVL(D.CON24, '-') AS CON24,
       NVL(D.SPEC25, '-') AS SPEC25, NVL(D.CON25, '-') AS CON25,
       NVL(D.SPEC26, '-') AS SPEC26, NVL(D.CON26, '-') AS CON26,
       NVL(D.SPEC27, '-') AS SPEC27, NVL(D.CON27, '-') AS CON27,
       NVL(D.SPEC28, '-') AS SPEC28, NVL(D.CON28, '-') AS CON28,
       NVL(D.SPEC29, '-') AS SPEC29, NVL(D.CON29, '-') AS CON29,
       NVL(D.SPEC30, '-') AS SPEC30, NVL(D.CON30, '-') AS CON30,
       NVL(D.KEY1, '-') AS KEY1, NVL(D.VAL1, '-') AS VAL1,
       NVL(D.KEY2, '-') AS KEY2, NVL(D.VAL2, '-') AS VAL2,
       NVL(D.KEY3, '-') AS KEY3, NVL(D.VAL3, '-') AS VAL3,
       NVL(D.KEY4, '-') AS KEY4, NVL(D.VAL4, '-') AS VAL4,
       NVL(D.KEY5, '-') AS KEY5, NVL(D.VAL5, '-') AS VAL5,
       NVL(D.KEY6, '-') AS KEY6, NVL(D.VAL6, '-') AS VAL6,
       NVL(D.KEY7, '-') AS KEY7, NVL(D.VAL7, '-') AS VAL7,
       NVL(D.KEY8, '-') AS KEY8, NVL(D.VAL8, '-') AS VAL8,
       NVL(D.KEY9, '-') AS KEY9, NVL(D.VAL9, '-') AS VAL9,
       NVL(D.KEY10, '-') AS KEY10, NVL(D.VAL10, '-') AS VAL10,
       NVL(D.KEY11, '-') AS KEY11, NVL(D.VAL11, '-') AS VAL11,
       NVL(D.KEY12, '-') AS KEY12, NVL(D.VAL12, '-') AS VAL12,
       NVL(D.KEY13, '-') AS KEY13, NVL(D.VAL13, '-') AS VAL13,
       NVL(D.KEY14, '-') AS KEY14, NVL(D.VAL14, '-') AS VAL14,
       NVL(D.KEY15, '-') AS KEY15, NVL(D.VAL15, '-') AS VAL15,
       NVL(D.KEY16, '-') AS KEY16, NVL(D.VAL16, '-') AS VAL16,
       NVL(D.KEY17, '-') AS KEY17, NVL(D.VAL17, '-') AS VAL17,
       NVL(D.KEY18, '-') AS KEY18, NVL(D.VAL18, '-') AS VAL18,
       NVL(D.KEY19, '-') AS KEY19, NVL(D.VAL19, '-') AS VAL19,
       NVL(D.KEY20, '-') AS KEY20, NVL(D.VAL20, '-') AS VAL20
  FROM HDEL_DEFAULT.VARIANT_D D,
       HDEL_DEFAULT.VARIANT_H H
 WHERE H.HOUID = D.HOUID
   AND H.PID = '{pid}'
   AND H.VERSION IN ('{v1}', '{v2}')
 ORDER BY TO_NUMBER(H.VERSION), D.NO"""

    csv_path = CSV_DIR / f"{pid}_v{v1}_v{v2}_comparison.csv"
    excel_name = f"{pid}_v{v1}_v{v2}_comparison.xlsx"
    
    # CSV 저장 실행
    subprocess.run([
        sys.executable, str(SCRIPTS_DIR / "query_to_csv.py"),
        "--sql", sql, "--output", str(csv_path)
    ], check=True)
    
    # Excel 저장 실행
    subprocess.run([
        sys.executable, str(SCRIPTS_DIR / "query_to_excel.py"),
        "--sql", sql, "--output", excel_name
    ], check=True)
    
    excel_path = EXCEL_DIR / excel_name
    return csv_path, excel_path


def format_row_summary(row: Dict[str, str]) -> str:
    """
    행(Row) 데이터에서 의미 있는 SPEC/CON, KEY/VAL, ADDR/GOTO/REMARKS 정보를 요약하여 반환하는 함수입니다.
    
    :param row: 한 행의 딕셔너리 데이터
    :return: 요약된 텍스트 문자열
    """
    no = row.get('NO', '')
    addr = row.get('ADDR', '-')
    goto = row.get('GOTO', '-')
    remarks = row.get('REMARKS', '-')
    
    specs = []
    for i in range(1, 31):
        s = row.get(f'SPEC{i}', '-').strip()
        c = row.get(f'CON{i}', '-').strip()
        if s != '-' or c != '-':
            specs.append(f"SPEC{i}:{s}=CON{i}:{c}")
            
    keys = []
    for i in range(1, 21):
        k = row.get(f'KEY{i}', '-').strip()
        v = row.get(f'VAL{i}', '-').strip()
        if k != '-' or v != '-':
            keys.append(f"KEY{i}:{k}=VAL{i}:{v}")
            
    spec_str = ", ".join(specs) if specs else "조건없음"
    key_str = ", ".join(keys) if keys else "결과없음"
    
    return f"[NO:{no}] ADDR:{addr} | GOTO:{goto} | REMARKS:{remarks} | 조건: [{spec_str}] | 결과: [{key_str}]"


def analyze_diff(csv_path: Path, pid: str, v1: str, v2: str) -> str:
    """
    CSV 데이터를 읽어 두 버전 간의 차이점을 상세 분석하고 보고서 텍스트를 생성하는 함수입니다.
    
    :param csv_path: 비교 CSV 파일 경로
    :param pid: PID명
    :param v1: 버전 1
    :param v2: 버전 2
    :return: 분석 보고서 텍스트
    """
    v1_rows = []
    v2_rows = []
    
    with open(csv_path, 'r', encoding='utf-8-sig') as f:
        reader = csv.DictReader(f)
        for row in reader:
            ver = row.get('VERSION', '').strip()
            if ver == str(v1):
                v1_rows.append(row)
            elif ver == str(v2):
                v2_rows.append(row)
                
    lines = []
    lines.append(f"=== {pid} PID 버전 {v1} vs 버전 {v2} 비교 분석 보고서 ===")
    lines.append(f"버전 {v1} 전체 라인 수: {len(v1_rows)}행")
    lines.append(f"버전 {v2} 전체 라인 수: {len(v2_rows)}행")
    lines.append("=" * 60)
    
    v1_dict = {r['NO']: r for r in v1_rows}
    v2_dict = {r['NO']: r for r in v2_rows}
    
    all_nos = sorted(list(set(v1_dict.keys()) | set(v2_dict.keys())), key=lambda x: int(x) if x.isdigit() else x)
    diff_count = 0
    
    for no in all_nos:
        r1 = v1_dict.get(no)
        r2 = v2_dict.get(no)
        
        if r1 and not r2:
            lines.append(f"\n[삭제된 행] NO {no}")
            lines.append(f"  - v{v1} 내용: {format_row_summary(r1)}")
            diff_count += 1
        elif not r1 and r2:
            lines.append(f"\n[추가된 행] NO {no}")
            lines.append(f"  - v{v2} 내용: {format_row_summary(r2)}")
            diff_count += 1
        else:
            diff_cols = []
            cols_to_check = ['ADDR', 'GOTO', 'REMARKS'] + \
                            [f'SPEC{i}' for i in range(1, 31)] + \
                            [f'CON{i}' for i in range(1, 31)] + \
                            [f'KEY{i}' for i in range(1, 21)] + \
                            [f'VAL{i}' for i in range(1, 21)]
            
            for col in cols_to_check:
                val1 = r1.get(col, '-').strip()
                val2 = r2.get(col, '-').strip()
                if val1 != val2:
                    diff_cols.append((col, val1, val2))
                    
            if diff_cols:
                diff_count += 1
                lines.append(f"\n[변경된 행] NO {no}")
                lines.append(f"  - v{v1} 내용 요약: {format_row_summary(r1)}")
                lines.append(f"  - v{v2} 내용 요약: {format_row_summary(r2)}")
                lines.append("  - 변경된 컬럼 상세:")
                for col, val1, val2 in diff_cols:
                    lines.append(f"    * {col}: '{val1}' -> '{val2}'")
                    
    lines.append("\n" + "=" * 60)
    if diff_count == 0:
        lines.append(f"결론: 버전 {v1}과 버전 {v2} 간에 차이가 있는 행이 없습니다.")
    else:
        lines.append(f"결론: 버전 {v1}과 버전 {v2} 간 총 {diff_count}개 행에서 변경사항이 확인되었습니다.")
        
    return "\n".join(lines)


def main():
    """
    메인 인자 파싱 및 실행 흐름 제어 함수입니다.
    """
    parser = argparse.ArgumentParser(description="PID 버전 간 비교 분석 스크립트")
    parser.add_argument("--pid", required=True, help="조회할 PID명 (예: B181A01)")
    parser.add_argument("--v1", help="첫 번째 버전 (미입력 시 직전 버전)")
    parser.add_argument("--v2", help="두 번째 버전 (미입력 시 최신 버전)")
    
    args = parser.parse_args()
    pid = args.pid.strip()
    
    # 버전 지정이 안 된 경우 DB에서 최신 버전 자동 조회
    if not args.v1 or not args.v2:
        ver_list = fetch_pid_versions(pid)
        if len(ver_list) < 2:
            print(f"오류: PID '{pid}'의 비교 가능한 버전이 2개 미만입니다.")
            return
            
        # 정수 버전 기준 정렬
        sorted_vers = sorted(ver_list, key=lambda x: int(x['VERSION']) if x['VERSION'].isdigit() else 0)
        v1 = sorted_vers[-2]['VERSION']
        v2 = sorted_vers[-1]['VERSION']
        print(f"버전 미지정으로 자동 선택된 비교 버전: v{v1} vs v{v2}")
    else:
        v1 = args.v1.strip()
        v2 = args.v2.strip()
        
    print(f"\n[1/3] DB에서 {pid} (v{v1} vs v{v2}) 데이터를 조회 중입니다...")
    csv_path, excel_path = run_comparison_queries(pid, v1, v2)
    print(f" -> CSV 저장 완료: {csv_path}")
    print(f" -> Excel 저장 완료: {excel_path}")
    
    print(f"\n[2/3] 버전 차이점 비교 분석 중입니다...")
    report_text = analyze_diff(csv_path, pid, v1, v2)
    
    print(f"\n[3/3] 보고서 파일 저장 완료...")
    DOCS_DIR.mkdir(parents=True, exist_ok=True)
    report_path = DOCS_DIR / f"{pid}_v{v1}_v{v2}_diff_report.txt"
    with open(report_path, "w", encoding="utf-8") as f:
        f.write(report_text)
        
    print("\n" + report_text)
    print(f"\n[보고서 저장 위치]: {report_path}")


if __name__ == "__main__":
    main()
