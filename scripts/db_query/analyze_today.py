import pandas as pd


def print_record_detail(df: pd.DataFrame) -> None:
    """
    오늘 등록된 비표준 사양검토 데이터프레임의 각 레코드를 상세히 출력하는 함수
    :param df: 조회 결과 데이터프레임
    """
    print(f"==================================================")
    print(f"  금일(2026-08-11) 비표준 사양검토 등록 건 분석 (총 {len(df)}건)")
    print(f"==================================================\n")

    for idx, row in df.iterrows():
        reqno = row.get("요청번호", "")
        cdate = str(row.get("등록일", ""))
        stat = row.get("작업상태", "")
        dept = row.get("등록부서", "")
        nation = row.get("국내해외", "")
        filedname = row.get("현장명", "")
        sujunum = row.get("호기번호", "")
        ptype = row.get("기종", "")
        puse = row.get("용도", "")
        scope = row.get("작업구분", "")
        cat1 = row.get("대분류", "")
        cat2 = row.get("중분류", "")
        title = row.get("제목", "")
        req_title = row.get("검토요청내용", "")
        detail = row.get("상세내용", "")
        manager = row.get("작업담당자", "")
        reply_type = row.get("회신구분", "")
        memo = row.get("회신내용", "")

        print(f"[{idx+1}] 요청번호: {reqno}")
        print(f"  - 등록일시: {cdate}")
        print(f"  - 작업상태: {stat if pd.notna(stat) else '미지정/진행중'}")
        print(f"  - 등록부서: {dept} ({nation})")
        print(f"  - 현장명: {filedname}")
        print(f"  - 호기번호: {sujunum if pd.notna(sujunum) else '미지정'}")
        print(f"  - 기종/용도: {ptype} / {puse}")
        print(f"  - 분류: [작업구분] {scope} | [대분류] {cat1} | [중분류] {cat2}")
        print(f"  - 제목: {title}")
        print(f"  - 검토요청내용: {req_title}")
        print(f"  - 상세내용: {detail}")
        print(f"  - 작업담당자: {manager if pd.notna(manager) else '미지정'}")
        print(f"  - 회신구분/내용: {reply_type} / {memo if pd.notna(memo) else '없음'}")
        print("-" * 60)


def print_summary_stats(df: pd.DataFrame) -> None:
    """
    비표준 사양검토 데이터의 집계 요약 정보(부서별, 대분류별, 작업상태별)를 출력하는 함수
    :param df: 조회 결과 데이터프레임
    """
    print("\n==================================================")
    print("  집계 요약 정보")
    print("==================================================")

    print("\n1. 등록 부서별 건수:")
    print(df["등록부서"].value_counts(dropna=False).to_string())

    print("\n2. 대분류별 건수:")
    print(df["대분류"].value_counts(dropna=False).to_string())

    print("\n3. 기종별 건수:")
    print(df["기종"].value_counts(dropna=False).to_string())

    print("\n4. 국내/해외 구분별 건수:")
    print(df["국내해외"].value_counts(dropna=False).to_string())

    print("\n5. 작업담당자 지정 현황:")
    print(df["작업담당자"].value_counts(dropna=False).to_string())


def main():
    csv_file = "output_csv/20260811_today_dutyreview.csv"
    df = pd.read_csv(csv_file, encoding="utf-8-sig")
    print_record_detail(df)
    print_summary_stats(df)


if __name__ == "__main__":
    main()
