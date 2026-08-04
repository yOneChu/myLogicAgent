import pandas as pd

df = pd.read_csv('output_csv/result_v1.csv', encoding='utf-8-sig')

def parse_date(val):
    if pd.isna(val) or str(val).strip() == '' or str(val).lower() == 'nan':
        return pd.NaT
    val_str = str(val).split('.')[0].strip()
    if len(val_str) == 8:
        return pd.to_datetime(val_str, format='%Y%m%d', errors='coerce')
    elif len(val_str) == 14:
        return pd.to_datetime(val_str, format='%Y%m%d%H%M%S', errors='coerce')
    else:
        return pd.to_datetime(val_str, errors='coerce')

df['dt_등록일'] = df['등록일'].apply(parse_date)
df['dt_의뢰일'] = df['의뢰일'].apply(parse_date)
df['dt_접수일'] = df['접수일'].apply(parse_date)
df['dt_완료일'] = df['완료일'].apply(parse_date)

# 날짜 차이 (일)
df['등록_완료_소요일수'] = (df['dt_완료일'] - df['dt_등록일']).dt.total_seconds() / (24 * 3600)
df['접수_완료_소요일수'] = (df['dt_완료일'] - df['dt_접수일']).dt.total_seconds() / (24 * 3600)

with open('analysis_summary.txt', 'w', encoding='utf-8') as f:
    f.write("=== 비표준사양검토 일주일(2026-07-29 ~ 2026-08-04) 데이터 분석 요약 ===\n\n")
    
    f.write(f"1. 전체 등록 건수: {len(df)}건\n\n")
    
    f.write("2. 작업상태별 건수:\n")
    f.write(df['작업상태'].value_counts(dropna=False).to_string() + "\n\n")
    
    f.write("3. 일자별 등록 건수:\n")
    df['등록일자'] = df['등록일'].astype(str).str.slice(0, 8)
    f.write(df['등록일자'].value_counts().sort_index().to_string() + "\n\n")
    
    f.write("4. 등록부서별 건수:\n")
    f.write(df['등록부서'].value_counts(dropna=False).to_string() + "\n\n")
    
    f.write("5. 대분류(검토 유형)별 건수:\n")
    f.write(df['대분류'].value_counts(dropna=False).to_string() + "\n\n")
    
    f.write("6. 기종별 건수:\n")
    f.write(df['기종'].value_counts(dropna=False).to_string() + "\n\n")
    
    f.write("7. 작업담당자별 건수:\n")
    f.write(df['작업담당자'].value_counts(dropna=False).to_string() + "\n\n")
    
    completed = df[df['dt_완료일'].notna()]
    f.write(f"8. 리드타임 상세 분석 (완료 {len(completed)}건 대상):\n")
    f.write(f"  - 등록일 -> 완료일 평균 소요시간: {completed['등록_완료_소요일수'].mean():.2f}일 ({completed['등록_완료_소요일수'].mean()*24:.1f}시간)\n")
    f.write(f"  - 등록일 -> 완료일 최소/최대: {completed['등록_완료_소요일수'].min():.2f}일 / {completed['등록_완료_소요일수'].max():.2f}일\n")
    f.write(f"  - 접수일 -> 완료일 평균 소요시간: {completed['접수_완료_소요일수'].mean():.2f}일 ({completed['접수_완료_소요일수'].mean()*24:.1f}시간)\n")
    f.write(f"  - 접수일 -> 완료일 최소/최대: {completed['접수_완료_소요일수'].min():.2f}일 / {completed['접수_완료_소요일수'].max():.2f}일\n\n")
    
    f.write("9. 전체 35건 상세 테이블 요약:\n")
    cols = ['요청번호', '등록일', '완료일', '작업상태', '등록부서', '대분류', '기종', '작업담당자', '검토요청내용']
    f.write(df[cols].to_string() + "\n")

print("Saved analysis_summary.txt successfully.")
