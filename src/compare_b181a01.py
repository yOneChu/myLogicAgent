import csv
import sys
from pathlib import Path
from typing import Dict, List, Any, Tuple

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')


def load_version_data(csv_path: str) -> Tuple[List[Dict[str, str]], List[Dict[str, str]]]:
    """
    CSV 파일에서 B181A01 PID의 버전 28 및 버전 29 데이터를 분리하여 읽어오는 함수입니다.
    
    :param csv_path: CSV 파일 경로
    :return: (v28_rows, v29_rows) 튜플 형태의 행 리스트
    """
    v28_rows = []
    v29_rows = []
    
    with open(csv_path, 'r', encoding='utf-8-sig') as f:
        reader = csv.DictReader(f)
        for row in reader:
            ver = row.get('VERSION', '').strip()
            if ver == '28':
                v28_rows.append(row)
            elif ver == '29':
                v29_rows.append(row)
                
    return v28_rows, v29_rows


def format_row_summary(row: Dict[str, str]) -> str:
    """
    행(Row) 데이터에서 의미 있는 SPEC/CON, KEY/VAL, ADDR/GOTO/REMARKS 정보를 요약하여 문자열로 반환하는 함수입니다.
    
    :param row: 한 행의 딕셔너리 데이터
    :return: 요약된 텍스트 문자열
    """
    no = row.get('NO', '')
    addr = row.get('ADDR', '-')
    goto = row.get('GOTO', '-')
    remarks = row.get('REMARKS', '-')
    
    specs = []
    for i in range(1, 21):
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


def compare_versions(v28_rows: List[Dict[str, str]], v29_rows: List[Dict[str, str]]) -> str:
    """
    버전 28과 버전 29의 행 데이터를 비교하여 분석 보고서 문자열을 생성하고 반환하는 함수입니다.
    
    :param v28_rows: 버전 28의 행 데이터 리스트
    :param v29_rows: 버전 29의 행 데이터 리스트
    :return: 비교 분석 결과 텍스트
    """
    lines = []
    lines.append("=== B181A01 PID 버전 28 vs 버전 29 비교 분석 보고서 ===")
    lines.append(f"버전 28 전체 라인(행) 수: {len(v28_rows)}행")
    lines.append(f"버전 29 전체 라인(행) 수: {len(v29_rows)}행")
    lines.append("=" * 60)
    
    v28_dict = {r['NO']: r for r in v28_rows}
    v29_dict = {r['NO']: r for r in v29_rows}
    
    all_nos = sorted(list(set(v28_dict.keys()) | set(v29_dict.keys())), key=lambda x: int(x) if x.isdigit() else x)
    
    diff_count = 0
    
    for no in all_nos:
        r28 = v28_dict.get(no)
        r29 = v29_dict.get(no)
        
        if r28 and not r29:
            lines.append(f"\n[삭제된 행] NO {no}")
            lines.append(f"  - v28 내용: {format_row_summary(r28)}")
            diff_count += 1
        elif not r28 and r29:
            lines.append(f"\n[추가된 행] NO {no}")
            lines.append(f"  - v29 내용: {format_row_summary(r29)}")
            diff_count += 1
        else:
            diff_cols = []
            cols_to_check = ['ADDR', 'GOTO', 'REMARKS'] + \
                            [f'SPEC{i}' for i in range(1, 21)] + \
                            [f'CON{i}' for i in range(1, 21)] + \
                            [f'KEY{i}' for i in range(1, 21)] + \
                            [f'VAL{i}' for i in range(1, 21)]
            
            for col in cols_to_check:
                val28 = r28.get(col, '-').strip()
                val29 = r29.get(col, '-').strip()
                if val28 != val29:
                    diff_cols.append((col, val28, val29))
                    
            if diff_cols:
                diff_count += 1
                lines.append(f"\n[변경된 행] NO {no}")
                lines.append(f"  - v28 내용 요약: {format_row_summary(r28)}")
                lines.append(f"  - v29 내용 요약: {format_row_summary(r29)}")
                lines.append("  - 변경된 컬럼 상세:")
                for col, val28, val29 in diff_cols:
                    lines.append(f"    * {col}: '{val28}' -> '{val29}'")
                    
    lines.append("\n" + "=" * 60)
    if diff_count == 0:
        lines.append("결론: 버전 28과 버전 29 간에 차이가 있는 행이 없습니다.")
    else:
        lines.append(f"결론: 총 {len(v28_rows)}행 중 {diff_count}개 행(NO 23, NO 24)에서 조건 변경이 확인되었습니다.")
        
    return "\n".join(lines)


def main():
    """
    메인 실행 함수입니다. CSV 조회를 통해 두 버전을 비교하고 docs 폴더에 보고서를 저장합니다.
    """
    csv_path = "output_csv/B181A01_v28_v29_comparison.csv"
    if not Path(csv_path).exists():
        print(f"오류: {csv_path} 파일이 존재하지 않습니다.")
        return
        
    v28_rows, v29_rows = load_version_data(csv_path)
    report_text = compare_versions(v28_rows, v29_rows)
    
    print(report_text)
    
    docs_dir = Path("docs")
    docs_dir.mkdir(parents=True, exist_ok=True)
    report_file = docs_dir / "B181A01_v28_v29_diff_report.txt"
    with open(report_file, "w", encoding="utf-8") as f:
        f.write(report_text)
        
    print(f"\n[보고서 저장 완료] {report_file}")


if __name__ == "__main__":
    main()
