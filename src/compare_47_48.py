#!/usr/bin/env python3
"""
NO 47과 NO 48행 1:1 컬럼 전수 비교 스크립트
"""

import csv
import sys
from pathlib import Path

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')


def compare_47_and_48():
    project_root = Path(__file__).resolve().parent.parent
    
    # 1. 테스트 버전 (EL_PA103A_test.csv)
    test_csv = project_root / "output_csv" / "EL_PA103A_test.csv"
    with open(test_csv, 'r', encoding='utf-8-sig') as f:
        rows_test = list(csv.DictReader(f))

    r47_test = next((r for r in rows_test if r['NO'] == '47'), None)
    r48_test = next((r for r in rows_test if r['NO'] == '48'), None)

    print("==================================================")
    print("  [테스트 버전 VERSION=-1] NO 47 vs NO 48 전수 비교  ")
    print("==================================================")
    
    print("\n--- NO 47 (테스트 버전) 전체 데이터 ---")
    for k, v in r47_test.items():
        if v and v != '-':
            print(f"  {k}: '{v}'")

    print("\n--- NO 48 (테스트 버전) 전체 데이터 ---")
    for k, v in r48_test.items():
        if v and v != '-':
            print(f"  {k}: '{v}'")

    print("\n--- NO 47 vs NO 48 차이점 목록 (테스트 버전) ---")
    diffs = []
    for k in r47_test.keys():
        v47 = r47_test.get(k, '-').strip()
        v48 = r48_test.get(k, '-').strip()
        if v47 != v48:
            diffs.append((k, v47, v48))

    if not diffs:
        print("  🎉 NO 47과 NO 48은 모든 컬럼이 100% 동일합니다!")
    else:
        for d in diffs:
            print(f"  - 컬럼 [{d[0]}]: NO 47 = '{d[1]}' <---> NO 48 = '{d[2]}'")

    # 2. 운영 버전 (EL_PA103A.csv)
    prod_csv = project_root / "output_csv" / "EL_PA103A.csv"
    if prod_csv.exists():
        with open(prod_csv, 'r', encoding='utf-8-sig') as f:
            rows_prod = list(csv.DictReader(f))

        r47_prod = next((r for r in rows_prod if r['NO'] == '47'), None)
        r48_prod = next((r for r in rows_prod if r['NO'] == '48'), None)

        print("\n==================================================")
        print("  [운영 최신 버전] NO 47 vs NO 48 전수 비교  ")
        print("==================================================")
        
        diffs_prod = []
        for k in r47_prod.keys():
            v47 = r47_prod.get(k, '-').strip()
            v48 = r48_prod.get(k, '-').strip()
            if v47 != v48:
                diffs_prod.append((k, v47, v48))

        if not diffs_prod:
            print("  🎉 NO 47과 NO 48은 운영 버전에서도 모든 컬럼이 100% 동일합니다!")
        else:
            for d in diffs_prod:
                print(f"  - 컬럼 [{d[0]}]: NO 47 = '{d[1]}' <---> NO 48 = '{d[2]}'")


if __name__ == "__main__":
    compare_47_and_48()
