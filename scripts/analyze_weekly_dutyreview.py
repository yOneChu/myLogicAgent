import pandas as pd
import numpy as np

# Load dataset
df = pd.read_csv('output_csv/result_v1.csv', encoding='utf-8-sig')

print("=== 1. 기본 개요 ===")
print("전체 등록 건수:", len(df))

print("\n=== 2. 작업상태별 분포 ===")
print(df['작업상태'].value_counts(dropna=False))

print("\n=== 3. 등록부서별 현황 ===")
print(df['등록부서'].value_counts(dropna=False))

print("\n=== 4. 대분류별 현황 ===")
print(df['대분류'].value_counts(dropna=False))

print("\n=== 5. 기종별 현황 ===")
print(df['기종'].value_counts(dropna=False))

print("\n=== 6. 작업담당자별 현황 ===")
print(df['작업담당자'].value_counts(dropna=False))

# 리드타임 계산 함수
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

# 완료된 건 필터링
completed_df = df[df['dt_완료일'].notna()].copy()

print("\n=== 7. 리드타임 분석 ===")
print("전체 35건 중 완료 건수:", len(completed_df), "건 / 미완료(진행중):", len(df) - len(completed_df), "건")

if len(completed_df) > 0:
    # 1. 등록일 -> 완료일 (일 단위)
    completed_df['lead_reg_to_fin_days'] = (completed_df['dt_완료일'] - completed_df['dt_등록일']).dt.total_seconds() / (24 * 3600)
    # 2. 접수일 -> 완료일 (일 단위)
    completed_df['lead_acpt_to_fin_days'] = (completed_df['dt_완료일'] - completed_df['dt_접수일']).dt.total_seconds() / (24 * 3600)
    
    print("\n[등록일 ~ 완료일 리드타임 (일)]")
    print(f"평균: {completed_df['lead_reg_to_fin_days'].mean():.2f}일")
    print(f"최소: {completed_df['lead_reg_to_fin_days'].min():.2f}일")
    print(f"최대: {completed_df['lead_reg_to_fin_days'].max():.2f}일")
    print(f"중앙값: {completed_df['lead_reg_to_fin_days'].median():.2f}일")
    
    print("\n[접수일 ~ 완료일 리드타임 (일)]")
    print(f"평균: {completed_df['lead_acpt_to_fin_days'].mean():.2f}일")
    print(f"최소: {completed_df['lead_acpt_to_fin_days'].min():.2f}일")
    print(f"최대: {completed_df['lead_acpt_to_fin_days'].max():.2f}일")

print("\n=== 8. 일자별 등록 현황 ===")
df['등록일자'] = df['등록일'].astype(str).str.slice(0, 8)
print(df['등록일자'].value_counts().sort_index())

print("\n=== 9. 상세 레코드 출력 (일부) ===")
print(df[['요청번호', '등록일', '완료일', '작업상태', '등록부서', '대분류', '작업담당자', '검토요청내용']].head(10))
