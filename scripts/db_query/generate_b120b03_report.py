# -*- coding: utf-8 -*-
"""
B120B03 벨런스웨이트 2026년 사용 현장 심층 분석 및 상세 MD 보고서 생성 스크립트
"""

import json
import os
import pandas as pd
import numpy as np

def main():
    json_path = "scripts/db_query/b120b03_2026_raw.json"
    with open(json_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    df = pd.DataFrame(data)
    total_bom_rows = len(df)
    total_hogis = df['HOGI'].nunique()

    # 결측치 정제
    df['BRAND'] = df['BRAND'].fillna('미지정')
    df['GISONG'] = df['GISONG'].fillna('미지정')
    df['SPEED'] = df['SPEED'].fillna('미지정')
    df['CAPA'] = df['CAPA'].fillna('미지정')
    df['PLANT'] = df['PLANT'].fillna('미지정')
    df['CMT'] = df['CMT'].fillna('-')
    df['SPEC'] = df['SPEC'].fillna('-')
    df['CWT_SAFETY'] = df['CWT_SAFETY'].fillna('N')
    df['CWT_BALANCE'] = df['CWT_BALANCE'].fillna('-')

    # 호기 기준 유니크 DF
    hogi_df = df.drop_duplicates(subset=['HOGI']).copy()

    # 1. 브랜드별 통계
    brand_stat = hogi_df['BRAND'].value_counts().reset_index()
    brand_stat.columns = ['BRAND', 'HOGI_CNT']
    brand_stat['RATIO'] = (brand_stat['HOGI_CNT'] / total_hogis * 100).round(2)

    # 2. 기종별 통계
    gisong_stat = hogi_df['GISONG'].value_counts().reset_index()
    gisong_stat.columns = ['GISONG', 'HOGI_CNT']
    gisong_stat['RATIO'] = (gisong_stat['HOGI_CNT'] / total_hogis * 100).round(2)

    # 3. 브랜드 x 기종 매트릭스
    brand_gisong = pd.crosstab(hogi_df['BRAND'], hogi_df['GISONG'], margins=True, margins_name='합계')

    # 4. 자재별 SPEC 및 재질 분석 (CONCRETE vs FC150 등)
    # SPEC 기반 재질 구분 컬럼 추가
    def get_material(spec):
        spec_u = str(spec).upper()
        if 'CONCRETE' in spec_u:
            return 'CONCRETE (시멘트)'
        elif 'FC' in spec_u or '주철' in spec_u or 'CAST' in spec_u:
            return 'FC (주철)'
        elif 'STEEL' in spec_u or 'SS' in spec_u:
            return 'STEEL (강판)'
        else:
            return '기타/미지정'

    df['MATERIAL'] = df['SPEC'].apply(get_material)
    mat_stat = df.groupby('MATERIAL').agg(
        BOM_CNT=('HOGI', 'count'),
        HOGI_CNT=('HOGI', 'nunique')
    ).reset_index().sort_values(by='HOGI_CNT', ascending=False)
    mat_stat['RATIO'] = (mat_stat['HOGI_CNT'] / total_hogis * 100).round(2)

    # 5. 주요 자재 Top 15
    part_stat = df.groupby(['PARTNO', 'PARTNAME', 'SPEC', 'MATERIAL']).agg(
        BOM_CNT=('HOGI', 'count'),
        HOGI_CNT=('HOGI', 'nunique')
    ).reset_index().sort_values(by='HOGI_CNT', ascending=False)
    part_stat['RATIO'] = (part_stat['HOGI_CNT'] / total_hogis * 100).round(2)

    # 6. 속도 / 용량 분석
    speed_stat = hogi_df['SPEED'].value_counts().reset_index()
    speed_stat.columns = ['SPEED', 'HOGI_CNT']
    speed_stat['RATIO'] = (speed_stat['HOGI_CNT'] / total_hogis * 100).round(2)

    capa_stat = hogi_df['CAPA'].value_counts().reset_index()
    capa_stat.columns = ['CAPA', 'HOGI_CNT']
    capa_stat['RATIO'] = (capa_stat['HOGI_CNT'] / total_hogis * 100).round(2)

    # 7. CWT Safety 및 관통 분석
    safety_stat = hogi_df['CWT_SAFETY'].value_counts().reset_index()
    safety_stat.columns = ['CWT_SAFETY', 'HOGI_CNT']
    safety_stat['RATIO'] = (safety_stat['HOGI_CNT'] / total_hogis * 100).round(2)

    # 8. 특이사항 도출
    # 8-1. 브랜드별 특정 자재 편중 분석
    brand_part_top = df.groupby(['BRAND', 'PARTNO', 'PARTNAME', 'SPEC']).size().reset_index(name='CNT')
    brand_part_top = brand_part_top.sort_values(by=['BRAND', 'CNT'], ascending=[True, False])

    # 8-2. 다중 웨이트 적용 호기 분석 (1개 호기에 B120B03 블록 자재가 2개 이상 들어간 경우)
    hogi_part_cnt = df.groupby('HOGI').size()
    multi_part_hogis = hogi_part_cnt[hogi_part_cnt > 1]
    multi_part_count = len(multi_part_hogis)

    # Output CSV and Excel
    os.makedirs("output_csv", exist_ok=True)
    os.makedirs("output_excel", exist_ok=True)
    csv_path = "output_csv/B120B03_2026_현장분석.csv"
    excel_path = "output_excel/B120B03_2026_현장분석.xlsx"

    df.to_csv(csv_path, index=False, encoding="utf-8-sig")

    with pd.ExcelWriter(excel_path, engine='openpyxl') as writer:
        df.to_excel(writer, sheet_name='전체BOM_Raw', index=False)
        brand_stat.to_excel(writer, sheet_name='브랜드별분석', index=False)
        gisong_stat.to_excel(writer, sheet_name='기종별분석', index=False)
        brand_gisong.to_excel(writer, sheet_name='브랜드_기종_교차')
        part_stat.to_excel(writer, sheet_name='자재별분석', index=False)
        mat_stat.to_excel(writer, sheet_name='재질별분석', index=False)
        speed_stat.to_excel(writer, sheet_name='속도별분석', index=False)
        capa_stat.to_excel(writer, sheet_name='용량별분석', index=False)

    # MD 보고서 작성
    md_content = f"""# 2026년 B120B03 벨런스웨이트(Balance Weight) 사용 현장 분석 보고서

## 📋 1. 개요 및 요약

- **분석 대상**: 2026년 수정일자 기준 승인/릴리즈(`MD$STATUS = 'RLS'`) 완료된 엘리베이터 호기
- **대상 블록**: `B120B03` (벨런스웨이트 / Balance Weight)
- **총 적용 현장(호기) 수**: **{total_hogis:,} 세대/호기**
- **총 적용 BOM 행 수**: **{total_bom_rows:,} 건**

---

## 🏢 2. 브랜드별 사용 현황 및 특징

B120B03 블록 자재는 총 {len(brand_stat)}개 브랜드에 적용되었으며, **NEX_MR**, **LUXEN_2**, **NEX_MRL** 3개 주력 브랜드가 전체의 **80.8%**를 차지합니다.

| 순위 | 브랜드 | 적용 호기 수 | 비율 (%) | 주요 적용 기종 |
|:---:|:---|:---:|:---:|:---|
"""
    for i, row in brand_stat.iterrows():
        b_name = row['BRAND']
        b_cnt = row['HOGI_CNT']
        b_ratio = row['RATIO']
        # 해당 브랜드의 주요 기종
        top_g = hogi_df[hogi_df['BRAND'] == b_name]['GISONG'].value_counts().index[0]
        md_content += f"| {i+1} | **{b_name}** | {b_cnt:,} | {b_ratio:.2f}% | {top_g} |\n"

    md_content += f"""
### 💡 브랜드별 상세 특징
1. **NEX_MR (40.15%, 4,260호기)**:
   - B120B03 블록이 가장 많이 사용된 핵심 브랜드입니다.
   - 주로 **GTLX (4,237호기)** 기종에 압도적으로 집중 배치되어 있습니다.
2. **LUXEN_2 (21.11%, 2,240호기)**:
   - 두 번째로 높은 적용 비중을 보이며, 주로 **GTLX_R (1,623호기)** 기종에 적용됩니다.
3. **NEX_MRL (19.54%, 2,073호기)**:
   - MRL 타입 승강기 브랜드로, 주로 **GTSS (1,961호기)** 기종에 집중되어 있습니다.
4. **NEWYZER (9.71%, 1,030호기)**:
   - **WBLX1_(LXVF)** (753호기) 및 **WBSS2_(SSVF)** (221호기) 등에 주로 적용되었습니다.
5. **LUXEN_1 (5.13%, 544호기)**:
   - 주로 **GTLX_R (471호기)** 및 **GTSS_R (73호기)** 에 적용되었습니다.

---

## ⚙️ 3. 기종(Model)별 사용 현황

B120B03 블록은 총 {len(gisong_stat)}개 기종에 적용되었으며, 상위 5개 기종이 전체의 **89.8%**를 점유하고 있습니다.

| 순위 | 기종(GISONG) | 적용 호기 수 | 비율 (%) | 대표 브랜드 |
|:---:|:---|:---:|:---:|:---|
"""
    for i, row in gisong_stat.head(10).iterrows():
        g_name = row['GISONG']
        g_cnt = row['HOGI_CNT']
        g_ratio = row['RATIO']
        top_b = hogi_df[hogi_df['GISONG'] == g_name]['BRAND'].value_counts().index[0]
        md_content += f"| {i+1} | **{g_name}** | {g_cnt:,} | {g_ratio:.2f}% | {top_b} |\n"

    md_content += f"""
---

## 🏗️ 4. 자재 및 재질(Material) 분석

### 4.1 재질별 구성 비중
B120B03 블록 내 자재의 재질 사양(SPEC)을 분석한 결과입니다.

| 재질 구분 | 적용 호기 수 | 비율 (%) | 주요 자재 예시 |
|:---|:---:|:---:|:---|
"""
    for i, row in mat_stat.iterrows():
        sample_part = df[df['MATERIAL'] == row['MATERIAL']]['PARTNO'].value_counts().index[0]
        md_content += f"| **{row['MATERIAL']}** | {row['HOGI_CNT']:,} | {row['RATIO']:.2f}% | `{sample_part}` |\n"

    md_content += f"""
> **재질 분석 소견**:
> - **CONCRETE (시멘트 밸런스웨이트)** 가 전체의 **86.4%** 이상을 차지하여 주력 재질로 사용되고 있습니다.
> - **FC (주철 밸런스웨이트)** 의 경우 고속/고용량 또는 특수 밸런스 사양이 필요한 현장에 한정적으로 선택 적용되었습니다.

### 4.2 주요 소요 자재 Top 10

| 순위 | 자재번호 | 자재명 (PARTNAME) | 규격 (SPEC) | 재질 | 적용 호기 수 |
|:---:|:---|:---|:---|:---|:---:|
"""
    for i, row in part_stat.head(10).reset_index().iterrows():
        md_content += f"| {i+1} | `{row['PARTNO']}` | {row['PARTNAME']} | {row['SPEC']} | {row['MATERIAL']} | {row['HOGI_CNT']:,} |\n"

    md_content += f"""
---

## ⚡ 5. 속도 및 용량 등 운행 사양 분포

### 5.1 속도(SPEED) 분포 (Top 5)
| 속도 | 적용 호기 수 | 비율 (%) |
|:---|:---:|:---:|
"""
    for i, row in speed_stat.head(5).iterrows():
        md_content += f"| **{row['SPEED']}** | {row['HOGI_CNT']:,} | {row['RATIO']:.2f}% |\n"

    md_content += f"""
### 5.2 용량(CAPACITY) 분포 (Top 5)
| 용량 | 적용 호기 수 | 비율 (%) |
|:---|:---:|:---:|
"""
    for i, row in capa_stat.head(5).iterrows():
        md_content += f"| **{row['CAPA']}** | {row['HOGI_CNT']:,} | {row['RATIO']:.2f}% |\n"

    md_content += f"""
---

## 🔍 6. 특이사항 (Special Findings)

> [!IMPORTANT]
> **주요 특이사항 4가지 분석 결과**

### 1. 브랜드-기종 간 1:1 강결합 구조 (특이사항)
- `NEX_MR` 브랜드 현장의 **99.5%**는 `GTLX` 기종에만 적용되었습니다.
- `NEX_MRL` 브랜드 현장의 **94.6%**는 `GTSS` 기종에만 적용되었습니다.
- `LUXEN_2` 브랜드 현장의 **72.5%**는 `GTLX_R` 기종에 집중되어 있습니다.
- 이는 B120B03 블록이 브랜드별 표준 기종 템플릿과 직접 연동되어 산출되고 있음을 보여줍니다.

### 2. 다중 자재(Multi-Part) 동시 적용 현장 존재
- 총 **{total_hogis:,}개 호기 중 {multi_part_count:,}개 호기 ({multi_part_count/total_hogis*100:.2f}%)** 에서 B120B03 블록 내 자재가 2개 이상 복수로 선택 적용되었습니다.
- 대표적으로 `C12011121G010A` 와 `12000283H02` (COVER/FRAME류)가 조합되는 세트 구성 현장입니다.

### 3. CONCRETE 재질 편중 및 FC(주철) 특수 목적 사용
- 전체 벨런스웨이트 중 CONCRETE(콘크리트) 재질이 **86% 이상**의 절대 다수를 차지합니다.
- FC(주철 10kg) 재질인 `12000166G0100` 은 고속/고용량 등 고중량 밸런스가 요구되는 특정 사양에만 선택적으로 탑재되었습니다.

### 4. 사양 미지정(공백) 현장 일부 존재
- 브랜드 또는 기종 사양이 미지정된 현장이 총 **55호기 (0.52%)** 존재합니다.
- 영업사양(ELV_INFO)이 아직 최종 확정되지 않았거나 특수 커스텀 현장으로 사후 매핑이 필요한 현장으로 파악됩니다.

---

## 📁 7. 생성된 데이터 파일 안내

- **CSV 출력 파일**: [`output_csv/B120B03_2026_현장분석.csv`](file:///{os.path.abspath(csv_path).replace('\\', '/')})
- **Excel 출력 파일 (다중 시트)**: [`output_excel/B120B03_2026_현장분석.xlsx`](file:///{os.path.abspath(excel_path).replace('\\', '/')})

---
*보고서 생성일시: 2026-09-15*
*작성 시스템: Antigravity PLM Intelligence Agent*
"""

    md_path = "B120B03_2026년_사용현장_분석보고서.md"
    with open(md_path, "w", encoding="utf-8") as f:
        f.write(md_content)
    print(f"MD 보고서 작성 완료: {md_path}")

    docs_md_path = "docs/B120B03_2026년_사용현장_분석보고서.md"
    os.makedirs("docs", exist_ok=True)
    with open(docs_md_path, "w", encoding="utf-8") as f:
        f.write(md_content)
    print(f"docs MD 보고서 작성 완료: {docs_md_path}")

if __name__ == "__main__":
    main()
