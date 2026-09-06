# -*- coding: utf-8 -*-
"""
2026년 A101A 블럭 브랜드별 통계 분석 및 인사이트 도출 스크립트
작성일: 2026-09-05
"""

import os
import pandas as pd
import numpy as np

# 파이썬 주석: 공통 output_csv 경로에서 파일 로드 및 분석 수행 함수
def analyze_brand_data(csv_path: str):
    """
    수집된 A101A CSV 데이터를 기반으로 브랜드별 다각도 통계를 집계하는 주요 함수
    """
    if not os.path.exists(csv_path):
        print(f"파일이 존재하지 않습니다: {csv_path}")
        return None

    df = pd.read_csv(csv_path, encoding='utf-8-sig')
    print(f"전체 수집 행 수: {len(df):,}건")
    print(f"컬럼 목록: {list(df.columns)}")

    # 1. 브랜드별 호기 수 & 자재 수배 건수
    brand_summary = df.groupby('BRAND').agg(
        PROD_COUNT=('PARENTNO', 'nunique'),
        TOTAL_BOM_COUNT=('PARTNO', 'count')
    ).reset_index()

    brand_summary['PROD_RATIO (%)'] = (brand_summary['PROD_COUNT'] / df['PARENTNO'].nunique() * 100).round(2)
    brand_summary['BOM_RATIO (%)'] = (brand_summary['TOTAL_BOM_COUNT'] / len(df) * 100).round(2)
    brand_summary = brand_summary.sort_values(by='PROD_COUNT', ascending=False)

    print("\n[1] 브랜드별 현장(호기) 수 및 수배 건수:")
    print(brand_summary.to_string(index=False))

    # 2. 브랜드별 x 기종(GISONG) 크로스 분석
    brand_gisong = df.groupby(['BRAND', 'GISONG'])['PARENTNO'].nunique().unstack(fill_value=0)
    print("\n[2] 브랜드 x 기종별 현장 수:")
    print(brand_gisong)

    # 3. 브랜드별 x 속도(EL_ASPD) 크로스 분석
    brand_spd = df.groupby(['BRAND', 'EL_ASPD'])['PARENTNO'].nunique().unstack(fill_value=0)
    print("\n[3] 브랜드 x 속도대별 현장 수:")
    print(brand_spd)

    # 4. 브랜드별 세부 블록(BLOCKNO) 수배 분포
    brand_block = df.groupby(['BRAND', 'BLOCKNO'])['PARTNO'].count().unstack(fill_value=0)
    print("\n[4] 브랜드 x 세부 블록 수배 건수:")
    print(brand_block)

    # 5. 브랜드별 주요 수배 자재 Top 5
    print("\n[5] 브랜드별 수배 자재 Top 5:")
    for brand in df['BRAND'].unique():
        b_df = df[df['BRAND'] == brand]
        top_parts = b_df.groupby(['PARTNO', 'PARTNAME'])['PARENTNO'].nunique().reset_index()
        top_parts = top_parts.sort_values(by='PARENTNO', ascending=False).head(5)
        print(f"\n--- 브랜드: {brand} (총 호기 수: {b_df['PARENTNO'].nunique()}) ---")
        print(top_parts.to_string(index=False))

    return {
        "summary": brand_summary,
        "gisong": brand_gisong,
        "speed": brand_spd,
        "block": brand_block
    }

if __name__ == "__main__":
    csv_file = "output_csv/a101a_brand_analysis_2026.csv"
    analyze_brand_data(csv_file)
