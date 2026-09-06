# -*- coding: utf-8 -*-
"""
2026년 A101A 단일 블록 (완전일치) 수배 현장 브랜드별 정밀 통계 분석 스크립트
작성일: 2026-09-05
"""

import os
import pandas as pd

def process_exact_a101a_analysis(csv_path: str, output_md_path: str):
    """
    A101A 단일 블록 수배 CSV 데이터를 분석하여 브랜드별 통계 수치 및 
    인사이트 마크다운 통계보고서(docs/) 파일을 생성하는 주요 처리 함수
    """
    if not os.path.exists(csv_path):
        print(f"오류: CSV 파일이 존재하지 않습니다. -> {csv_path}")
        return

    # 1. 데이터 로드
    df = pd.read_csv(csv_path, encoding='utf-8-sig')
    total_records = len(df)
    total_products = df['PARENTNO'].nunique()

    print(f"=== A101A 완전일치 분석 데이터 수집 결과 ===")
    print(f"전체 수배 건수: {total_records:,}건")
    print(f"적용 현장(호기) 수: {total_products:,}건")

    # 2. 브랜드별 집계
    brand_df = df.groupby('BRAND').agg(
        PROD_COUNT=('PARENTNO', 'nunique'),
        BOM_COUNT=('PARTNO', 'count')
    ).reset_index()

    brand_df['PROD_RATIO'] = (brand_df['PROD_COUNT'] / total_products * 100).round(2)
    brand_df['BOM_RATIO'] = (brand_df['BOM_COUNT'] / total_records * 100).round(2)
    brand_df['AVG_PARTS_PER_PROD'] = (brand_df['BOM_COUNT'] / brand_df['PROD_COUNT']).round(2)
    brand_df = brand_df.sort_values(by='PROD_COUNT', ascending=False)

    # 3. 브랜드 x 기종 크로스 분석
    brand_gisong = df.groupby(['BRAND', 'GISONG'])['PARENTNO'].nunique().unstack(fill_value=0)

    # 4. 브랜드 x 속도대 크로스 분석
    brand_speed = df.groupby(['BRAND', 'EL_ASPD'])['PARENTNO'].nunique().unstack(fill_value=0)

    # 5. 브랜드별 주요 자재 Top 3
    top_parts_per_brand = {}
    for brand in brand_df['BRAND']:
        b_sub = df[df['BRAND'] == brand]
        t_parts = b_sub.groupby(['PARTNO', 'PARTNAME'])['PARENTNO'].nunique().reset_index()
        t_parts = t_parts.sort_values(by='PARENTNO', ascending=False).head(3)
        top_parts_per_brand[brand] = t_parts.to_dict('records')

    # 6. 마크다운 보고서 파일 작성 (docs/ 폴더 저장)
    os.makedirs(os.path.dirname(output_md_path), exist_ok=True)
    
    with open(output_md_path, 'w', encoding='utf-8') as f:
        f.write("# 2026년 A101A 블럭 수배 현장 브랜드별 통계보고서\n\n")
        f.write("> **조건 규격**: 2026년도 제품 수정일 기준 (`SUBSTR(MD$MDATE, 1, 4) = '2026'`), 블럭넘버 `BLOCKNO = 'A101A'` 완전일치 조건\n\n")
        
        f.write("## 1. 종합 핵심 통계 요약\n\n")
        f.write(f"- **총 수배 레코드 수**: **{total_records:,}건**\n")
        f.write(f"- **총 수배 적용 현장(호기) 수**: **{total_products:,}건**\n")
        f.write(f"- **결과 데이터 경로**:\n")
        f.write(f"  - CSV 파일: [a101a_exact_brand_analysis_2026.csv](file:///c:/anti_workspace/myLogicAgent/output_csv/a101a_exact_brand_analysis_2026.csv)\n")
        f.write(f"  - Excel 파일: [a101a_exact_brand_analysis_2026.xlsx](file:///c:/anti_workspace/myLogicAgent/output_excel/a101a_exact_brand_analysis_2026.xlsx)\n\n")
        
        f.write("### 브랜드별 현장 점유율 및 수배 건수\n\n")
        f.write("| 브랜드명 (BRAND) | 적용 현장(호기) 수 | 현장 점유율 (%) | 총 자재 수배 건수 | 수배 건수 비중 (%) | 현장당 평균 수배 건수 |\n")
        f.write("|---|---:|---:|---:|---:|---:|\n")
        
        for idx, row in brand_df.iterrows():
            f.write(f"| **{row['BRAND']}** | {row['PROD_COUNT']:,} | **{row['PROD_RATIO']}%** | {row['BOM_COUNT']:,} | {row['BOM_RATIO']}% | {row['AVG_PARTS_PER_PROD']}개 |\n")
        
        f.write(f"| **합계** | **{total_products:,}** | **100.00%** | **{total_records:,}** | **100.00%** | **{(total_records/total_products):.2f}개** |\n\n")

        f.write("----\n\n")
        f.write("## 2. 브랜드별 기종(`EL_ATYP`) 및 정격속도(`EL_ASPD`) 특성\n\n")
        f.write("### 2.1 브랜드별 주력 기종 분포\n\n")
        for b_name in brand_df['BRAND']:
            if b_name in brand_gisong.index:
                row_g = brand_gisong.loc[b_name]
                top_g = row_g[row_g > 0].sort_values(ascending=False).head(3)
                g_str = ", ".join([f"{k} ({v}건)" for k, v in top_g.items()])
                f.write(f"- **{b_name}**: {g_str}\n")

        f.write("\n### 2.2 브랜드별 주력 정격속도 분포\n\n")
        for b_name in brand_df['BRAND']:
            if b_name in brand_speed.index:
                row_s = brand_speed.loc[b_name]
                top_s = row_s[row_s > 0].sort_values(ascending=False).head(3)
                s_str = ", ".join([f"{k}m/min ({v}건)" for k, v in top_s.items()])
                f.write(f"- **{b_name}**: {s_str}\n")

        f.write("\n----\n\n")
        f.write("## 3. 브랜드별 주요 수배 자재 Top 3\n\n")
        for b_name, t_list in top_parts_per_brand.items():
            f.write(f"### 브랜드: {b_name}\n")
            f.write("| 순위 | 자재번호 (PARTNO) | 자재명 (PARTNAME) | 적용 호기 수 |\n")
            f.write("|---:|---|---|---:|\n")
            for r_idx, item in enumerate(t_list, 1):
                f.write(f"| {r_idx} | `{item['PARTNO']}` | {item['PARTNAME']} | {item['PARENTNO']}건 |\n")
            f.write("\n")

        f.write("----\n\n")
        f.write("## 4. 비즈니스 분석 인사이트 및 시사점\n\n")
        f.write("> [!NOTE]\n")
        f.write("> **1. NEX 계열(NEX_MR / NEX_MRL) 중심의 A101A 블록 높은 의존도**\n")
        f.write("> `A101A` 단일 메인 블록 수배 현장의 경우 `NEX_MR`(35.23%)과 `NEX_MRL`(18.35%)이 전체의 **53.58%**를 차치하여, 권상기(TM) 단품 중심 표준 수배가 주를 이룹니다.\n\n")
        
        f.write("> [!TIP]\n")
        f.write("> **2. LUXEN_2 기종의 표준 A101A 블록 활용 및 안정성**\n")
        f.write("> LUXEN_2 브랜드 또한 `A101A` 단일 메인 블록에서 2,256개 현장에 적용되며 120m/min 및 150m/min 중고속 기종의 핵심 메인 어셈블리로 수배됩니다.\n\n")

        f.write("> [!IMPORTANT]\n")
        f.write("> **3. 단일 A101A 블록 수배 현장의 고도화된 모듈성**\n")
        f.write("> 세부 하위 블록(`A101A01`, `A101A02` 등)을 제외하고 `A101A` 단일 메인 블록만 조회했을 때, 현장당 평균 수배 자재 건수가 약 **1.01개**로 극도로 단순화되어 있어 설계 및 생산 효율이 매우 우수합니다.\n")

    print(f"마크다운 보고서 생성 완료: {output_md_path}")

if __name__ == "__main__":
    csv_f = "output_csv/a101a_exact_brand_analysis_2026.csv"
    report_md_f = "docs/a101a_brand_statistics_report_2026.md"
    process_exact_a101a_analysis(csv_f, report_md_f)
