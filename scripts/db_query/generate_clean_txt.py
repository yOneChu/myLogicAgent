import pandas as pd


def generate_clean_report():
    """
    CSV 파일 데이터를 읽어 clean한 UTF-8 텍스트 분석 보고서를 생성하는 함수
    """
    df = pd.read_csv("output_csv/20260811_today_dutyreview.csv", encoding="utf-8-sig")

    with open("today_analysis_clean.txt", "w", encoding="utf-8") as f:
        f.write("==================================================\n")
        f.write(f"  금일(2026-08-11) 비표준 사양검토 분석 보고서 (총 {len(df)}건)\n")
        f.write("==================================================\n\n")

        for idx, row in df.iterrows():
            f.write(f"[{idx+1}] 요청번호: {row.get('요청번호')}\n")
            f.write(f"  - 등록일시: {row.get('등록일')}\n")
            f.write(f"  - 작업상태: {row.get('작업상태')}\n")
            f.write(
                f"  - 등록부서: {row.get('등록부서')} ({row.get('국내해외')})\n"
            )
            f.write(f"  - 현장명: {row.get('현장명')}\n")
            f.write(f"  - 호기번호: {row.get('호기번호')}\n")
            f.write(
                f"  - 기종/용도: {row.get('기종')} / {row.get('용도')}\n"
            )
            f.write(
                f"  - 분류: [작업구분] {row.get('작업구분')} | [대분류] {row.get('대분류')} | [중분류] {row.get('중분류')}\n"
            )
            f.write(f"  - 제목: {row.get('제목')}\n")
            f.write(f"  - 검토요청내용: {row.get('검토요청내용')}\n")
            f.write(f"  - 상세내용: {row.get('상세내용')}\n")
            f.write(f"  - 작업담당자: {row.get('작업담당자')}\n")
            f.write(
                f"  - 회신구분/내용: {row.get('회신구분')} / {row.get('회신내용')}\n"
            )
            f.write("-" * 60 + "\n")

        f.write("\n=== 1. 등록부서별 현황 ===\n")
        f.write(df["등록부서"].value_counts(dropna=False).to_string() + "\n")

        f.write("\n=== 2. 대분류별 현황 ===\n")
        f.write(df["대분류"].value_counts(dropna=False).to_string() + "\n")

        f.write("\n=== 3. 기종별 현황 ===\n")
        f.write(df["기종"].value_counts(dropna=False).to_string() + "\n")

        f.write("\n=== 4. 국내/해외 구분 ===\n")
        f.write(df["국내해외"].value_counts(dropna=False).to_string() + "\n")

        f.write("\n=== 5. 작업담당자 지정 현황 ===\n")
        f.write(df["작업담당자"].value_counts(dropna=False).to_string() + "\n")


if __name__ == "__main__":
    generate_clean_report()
