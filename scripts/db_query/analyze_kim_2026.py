"""
2026년 김영환 담당 처리 완료(RLS) 전산화 요청 건 데이터를 분석하는 스크립트.

주요 기능:
    - CSV 파일(output_csv/2026_김영환_처리완료_전산화요청.csv)을 읽어와 다각도로 통계 분석
    - 월별, 작업구분별, 요청사유별, 등록자별 집계 결과를 출력
"""

import csv
from collections import Counter
from typing import Dict, List, Any

def analyze_requests(csv_path: str) -> Dict[str, Any]:
    """
    CSV 데이터 파일을 분석하여 다양한 통계 지표를 산출한다.

    Args:
        csv_path (str): 분석할 CSV 파일 경로

    Returns:
        Dict[str, Any]: 분석 결과를 담은 디셔너리
    """
    records: List[Dict[str, str]] = []
    with open(csv_path, 'r', encoding='utf-8-sig') as f:
        reader = csv.DictReader(f)
        for row in reader:
            records.append(row)

    total_cnt = len(records)
    
    # 완료월 기준 월별 집계
    mod_month_counter = Counter()
    # 등록월 기준 월별 집계
    cre_month_counter = Counter()
    # 작업구분 집계
    type_counter = Counter()
    # 요청사유 집계
    cause_counter = Counter()
    # 등록자 집계
    user_counter = Counter()
    # 구분(전기/기계) 집계
    part_counter = Counter()

    for r in records:
        mod_m = r.get('MOD_YYYYMM', '')
        if mod_m:
            mod_month_counter[mod_m] += 1
            
        cre_m = r.get('CRE_YYYYMM', '')
        if cre_m:
            cre_month_counter[cre_m] += 1
            
        req_type = r.get('REQ_TYPE') or '미지정'
        type_counter[req_type] += 1
        
        req_cause = r.get('REQ_CAUSE') or '미지정'
        cause_counter[req_cause] += 1
        
        user_name = r.get('REQ_USER_NAME') or r.get('REQ_USER_ID') or '미상'
        user_counter[user_name] += 1

        part = r.get('DESIGNPART') or '미지정'
        part_counter[part] += 1

    return {
        'total_cnt': total_cnt,
        'mod_month': dict(sorted(mod_month_counter.items())),
        'cre_month': dict(sorted(cre_month_counter.items())),
        'req_type': type_counter.most_common(),
        'req_cause': cause_counter.most_common(),
        'req_user': user_counter.most_common(10),
        'part': part_counter.most_common(),
        'records': records
    }

def main() -> None:
    """
    메인 실행 함수. 분석 결과를 요약하여 콘솔에 출력한다.
    """
    csv_path = "output_csv/2026_김영환_처리완료_전산화요청.csv"
    res = analyze_requests(csv_path)
    
    print(f"=== 2026년 김영환 담당 처리 완료(RLS) 전산화 요청 종합 분석 (총 {res['total_cnt']}건) ===")
    print("\n1. 완료월별 건수:")
    for k, v in res['mod_month'].items():
        print(f"  - {k[:4]}년 {k[4:]}월: {v}건")
        
    print("\n2. 작업구분(REQ_TYPE)별 건수:")
    for k, v in res['req_type']:
        print(f"  - {k}: {v}건 ({v/res['total_cnt']*100:.1f}%)")

    print("\n3. 구분(DESIGNPART)별 건수:")
    for k, v in res['part']:
        print(f"  - {k}: {v}건")

    print("\n4. 주요 요청사유별 건수 (Top 7):")
    for k, v in res['req_cause'][:7]:
        print(f"  - {k}: {v}건")

    print("\n5. 주요 요청자(Top 5):")
    for k, v in res['req_user'][:5]:
        print(f"  - {k}: {v}건")

if __name__ == '__main__':
    main()
