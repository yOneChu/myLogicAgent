"""
2026년에 등록된 김영환 담당/작업 전산화 요청 전체 데이터(80건)를 분석하는 스크립트.

주요 기능:
    - 진행 상태(상태코드: RLS=완료, CRT=작성/진행중 등)별 분류
    - 등록 월별, 작업구분별, 요청사유별, 요청자별 통계 집계
    - 진행 중인 건(CRT 등)의 상세 내역 별도 정리
    - 분석 결과를 docs/summary_kim_2026_all.txt 파일로 저장
"""

import csv
from collections import Counter
from typing import Dict, List, Any

def analyze_all_registered_requests(csv_path: str) -> None:
    """
    CSV 파일 데이터를 정밀 분석하여 상세 분석 요약 파일을 작성한다.

    Args:
        csv_path (str): 분석 대상 CSV 파일 경로
    """
    records: List[Dict[str, str]] = []
    with open(csv_path, "r", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        for r in reader:
            records.append(r)

    total_cnt = len(records)
    
    # 상태별 집계
    status_cnt = Counter(r.get('STATUS', '미지정') for r in records)
    
    # 등록월별 집계
    cre_month_cnt = Counter(r.get('CRE_YYYYMM', '') for r in records)
    
    # 작업구분별 집계
    type_cnt = Counter(r.get('REQ_TYPE', '미지정') for r in records)
    
    # 요청사유별 집계
    cause_cnt = Counter(r.get('REQ_CAUSE', '미지정') for r in records)
    
    # 요청자별 집계
    user_cnt = Counter(r.get('REQ_USER_NAME', '미상') for r in records)

    # 상태별 세부 목록 분리 (완료 RLS vs 진행/작성중 CRT 등)
    completed_list = [r for r in records if r.get('STATUS') == 'RLS']
    in_progress_list = [r for r in records if r.get('STATUS') != 'RLS']

    lines = []
    lines.append(f"2026년 등록 김영환 담당/작업 전산화 요청 종합 보고서 (총 {total_cnt}건)\n")
    lines.append("="*65)
    
    lines.append("\n[1] 처리 상태별 현황")
    lines.append(f"  - 완료 (RLS): {len(completed_list)}건 ({len(completed_list)/total_cnt*100:.1f}%)")
    lines.append(f"  - 진행중/작성중 (CRT): {len(in_progress_list)}건 ({len(in_progress_list)/total_cnt*100:.1f}%)")

    lines.append("\n[2] 등록 월별 현황 (등록일 기준)")
    for k in sorted(cre_month_cnt.keys()):
        if k:
            lines.append(f"  - {k[:4]}년 {k[4:]}월: {cre_month_cnt[k]}건")

    lines.append("\n[3] 작업구분(REQ_TYPE)별 현황")
    for k, v in type_cnt.most_common():
        lines.append(f"  - {k or '미지정'}: {v}건 ({v/total_cnt*100:.1f}%)")

    lines.append("\n[4] 요청사유(REQ_CAUSE)별 현황")
    for k, v in cause_cnt.most_common():
        lines.append(f"  - {k or '미지정'}: {v}건 ({v/total_cnt*100:.1f}%)")

    lines.append("\n[5] 주요 요청자 Top 10")
    for k, v in user_cnt.most_common(10):
        lines.append(f"  - {k or '미상'}: {v}건")

    lines.append("\n[6] 현재 진행중/작성중 (CRT) 건 상세 목록")
    lines.append("-"*65)
    if in_progress_list:
        for r in in_progress_list:
            reqno = r.get('REQNO', '')
            title = r.get('REQ_TITLE', '') or '제목없음'
            rtype = r.get('REQ_TYPE', '')
            uname = r.get('REQ_USER_NAME', '')
            cdate = r.get('CRE_DATE', '')
            lines.append(f"• [{reqno}] {title} | 작업구분: {rtype} | 요청자: {uname} | 등록일: {cdate[:8] if cdate else ''} | 상태: 진행중(CRT)")
    else:
        lines.append("  - 현재 진행 중인 건이 없습니다.")

    lines.append("\n[7] 최근 등록 완료 건 샘플 (최신 10건)")
    lines.append("-"*65)
    for r in completed_list[:10]:
        reqno = r.get('REQNO', '')
        title = r.get('REQ_TITLE', '') or '제목없음'
        rtype = r.get('REQ_TYPE', '')
        uname = r.get('REQ_USER_NAME', '')
        cdate = r.get('CRE_DATE', '')
        mdate = r.get('MOD_DATE', '')
        lines.append(f"• [{reqno}] {title} | 작업구분: {rtype} | 요청자: {uname} | 등록일: {cdate[:8] if cdate else ''} | 완료일: {mdate[:8] if mdate else ''}")

    with open("docs/summary_kim_2026_all.txt", "w", encoding="utf-8") as f:
        f.write("\n".join(lines))

    print("Comprehensive summary written to docs/summary_kim_2026_all.txt")

if __name__ == '__main__':
    analyze_all_registered_requests("output_csv/2026_등록_김영환_전산화요청_전체.csv")
