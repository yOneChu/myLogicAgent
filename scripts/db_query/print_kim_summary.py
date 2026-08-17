"""
분석 결과를 텍스트 파일(utf-8)로 출력하여 한글 텍스트를 정교하게 확인하는 스크립트.

주요 함수:
    generate_summary_file(): 종합 분석 결과를 summary_kim_2026.txt 파일로 저장한다.
"""

import csv
from collections import Counter

def generate_summary_file() -> None:
    """
    2026년 김영환 처리완료 전산화 요청 데이터를 상세 분석하여 summary 파일로 남긴다.
    """
    records = []
    with open("output_csv/2026_김영환_처리완료_전산화요청.csv", "r", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        for r in reader:
            records.append(r)

    total_cnt = len(records)
    mod_m_cnt = Counter(r.get('MOD_YYYYMM', '') for r in records)
    cre_m_cnt = Counter(r.get('CRE_YYYYMM', '') for r in records)
    type_cnt = Counter(r.get('REQ_TYPE', '') for r in records)
    cause_cnt = Counter(r.get('REQ_CAUSE', '') for r in records)
    user_cnt = Counter(r.get('REQ_USER_NAME', '') for r in records)
    part_cnt = Counter(r.get('DESIGNPART', '') for r in records)

    lines = []
    lines.append(f"2026년 김영환 담당 처리 완료(RLS) 전산화 요청 종합 현황 (총 {total_cnt}건)\n")
    lines.append("="*60)
    lines.append("[1] 월별 완료 건수")
    for k in sorted(mod_m_cnt.keys()):
        if k:
            lines.append(f"  - {k[:4]}년 {k[4:]}월: {mod_m_cnt[k]}건")

    lines.append("\n[2] 작업구분(REQ_TYPE)별 건수")
    for k, v in type_cnt.most_common():
        lines.append(f"  - {k or '미지정'}: {v}건 ({v/total_cnt*100:.1f}%)")

    lines.append("\n[3] 설계구분(DESIGNPART)별 건수")
    for k, v in part_cnt.most_common():
        lines.append(f"  - {k or '미지정'}: {v}건")

    lines.append("\n[4] 요청사유(REQ_CAUSE)별 건수")
    for k, v in cause_cnt.most_common():
        lines.append(f"  - {k or '미지정'}: {v}건 ({v/total_cnt*100:.1f}%)")

    lines.append("\n[5] 주요 요청자 Top 10")
    for k, v in user_cnt.most_common(10):
        lines.append(f"  - {k or '미상'}: {v}건")

    lines.append("\n[6] 대표 요청 목록 샘플 (최근 완료 순 15건)")
    lines.append("-"*60)
    for r in records[:15]:
        reqno = r.get('REQNO', '')
        title = r.get('REQ_TITLE', '') or '제목없음'
        rtype = r.get('REQ_TYPE', '')
        uname = r.get('REQ_USER_NAME', '')
        cdate = r.get('CRE_DATE', '')
        mdate = r.get('MOD_DATE', '')
        lines.append(f"• [{reqno}] {title} | 작업구분: {rtype} | 요청자: {uname} | 완료일: {mdate[:8] if mdate else ''}")

    with open("docs/summary_kim_2026.txt", "w", encoding="utf-8") as f:
        f.write("\n".join(lines))

    print("Summary created at docs/summary_kim_2026.txt")

if __name__ == '__main__':
    generate_summary_file()
