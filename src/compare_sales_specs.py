#!/usr/bin/env python3
"""
두 영업사양 CSV 파일(N09994L04_sales_20260826.csv, N09995L04_sales_20260826.csv)을 비교하여
값이 서로 다른 항목만 순차적으로 printf 형태로 출력하는 파이썬 스크립트.
"""

import csv
import sys
from pathlib import Path

# 표준 출력 인코딩을 UTF-8로 설정
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')


def read_sales_csv(file_path: Path) -> dict[str, str]:
    """
    영업사양 CSV 파일을 읽어 {특성코드: 값} 딕셔너리로 반환합니다.
    """
    data = {}
    with open(file_path, mode='r', encoding='utf-8-sig', newline='') as f:
        reader = csv.reader(f)
        header = next(reader, None)  # 헤더(특성코드, 값) 스킵
        for row in reader:
            if not row:
                continue
            code = row[0].strip() if len(row) > 0 else ""
            val = row[1].strip() if len(row) > 1 else ""
            if code:
                data[code] = val
    return data


def read_sales_csv_ordered(file_path: Path) -> tuple[dict[str, str], list[str]]:
    """
    영업사양 CSV 파일을 읽어 ({특성코드: 값}, [특성코드 순서 리스트]) 튜플을 반환합니다.
    """
    data = {}
    order = []
    with open(file_path, mode='r', encoding='utf-8-sig', newline='') as f:
        reader = csv.reader(f)
        header = next(reader, None)
        for row in reader:
            if not row:
                continue
            code = row[0].strip() if len(row) > 0 else ""
            val = row[1].strip() if len(row) > 1 else ""
            if code:
                if code not in data:
                    order.append(code)
                data[code] = val
    return data, order


def compare_and_print_diff(file1_path: Path, file2_path: Path):
    dict1, order1 = read_sales_csv_ordered(file1_path)
    dict2, order2 = read_sales_csv_ordered(file2_path)

    f1_name = file1_path.name
    f2_name = file2_path.name

    # 전체 특성코드 순서 보장 (file1의 순서 + file2에서 새로 등장한 코드)
    all_codes = list(order1)
    for code in order2:
        if code not in dict1 and code not in all_codes:
            all_codes.append(code)

    diff_count = 0
    print("=" * 110)
    print(f"영업사양 비교 시작: [{f1_name}] vs [{f2_name}]")
    print("=" * 110)
    # printf 스타일 헤더 출력
    print(f"{'No.':<6} | {'특성코드':<20} | {f1_name:<38} | {f2_name:<38}")
    print("-" * 110)

    for code in all_codes:
        val1 = dict1.get(code, "<미존재>")
        val2 = dict2.get(code, "<미존재>")

        # 값이 다른 경우만 차이점으로 출력
        if val1 != val2:
            diff_count += 1
            # 줄바꿈 문자가 있는 경우 한 줄 형태로 정형화
            display_val1 = val1.replace('\n', ' \\n ')
            display_val2 = val2.replace('\n', ' \\n ')
            
            # C style printf 포맷팅 출력
            print("%-6d | %-20s | %-38s | %-38s" % (diff_count, code, display_val1[:38], display_val2[:38]))

    print("-" * 110)
    print(f"비교 완료: 총 {diff_count} 건의 상이한 영업사양 항목이 발견되었습니다.")
    print("=" * 110)


def main():
    base_dir = Path(__file__).resolve().parent
    file1 = base_dir / "N09994L04_sales_20260826.csv"
    file2 = base_dir / "N09995L04_sales_20260826.csv"

    if not file1.exists() or not file2.exists():
        print(f"오류: 비교할 파일이 존재하지 않습니다.", file=sys.stderr)
        sys.exit(1)

    compare_and_print_diff(file1, file2)


if __name__ == "__main__":
    main()
