import csv
from collections import Counter, defaultdict
import json

csv_file = "output_csv/a101a_brand_analysis_2026.csv"

# 데이터 로드
with open(csv_file, 'r', encoding='utf-8-sig') as f:
    reader = csv.DictReader(f)
    rows = list(reader)

total_bom_rows = len(rows)
all_products = set(r['PARENTNO'] for r in rows if r['PARENTNO'])
total_distinct_products = len(all_products)

print(f"총 수배 행 수 (BOM Row Count): {total_bom_rows:,}건")
print(f"총 적용 현장(호기) 수 (Distinct Product Count): {total_distinct_products:,}개")

# 1. 브랜드별 집계
brand_products = defaultdict(set)
brand_bom_cnt = Counter()

for r in rows:
    b = r['BRAND'] if r['BRAND'] else '기타/미정'
    p = r['PARENTNO']
    brand_products[b].add(p)
    brand_bom_cnt[b] += 1

print("\n=== 1. 브랜드별 현장 수 및 BOM 수배 건수 ===")
brand_stats = []
for b, prod_set in sorted(brand_products.items(), key=lambda x: len(x[1]), reverse=True):
    p_cnt = len(prod_set)
    p_ratio = (p_cnt / total_distinct_products) * 100
    b_cnt = brand_bom_cnt[b]
    b_ratio = (b_cnt / total_bom_rows) * 100
    brand_stats.append({
        'brand': b,
        'prod_cnt': p_cnt,
        'prod_ratio': round(p_ratio, 2),
        'bom_cnt': b_cnt,
        'bom_ratio': round(b_ratio, 2)
    })
    print(f"- {b}: {p_cnt:,}개 호기 ({p_ratio:.2f}%) / {b_cnt:,}건 BOM ({b_ratio:.2f}%)")

# 2. 브랜드별 기종(GISONG) 분포
brand_gisong = defaultdict(lambda: defaultdict(set))
for r in rows:
    b = r['BRAND'] if r['BRAND'] else '기타/미정'
    g = r['GISONG'] if r['GISONG'] else '기타'
    p = r['PARENTNO']
    brand_gisong[b][g].add(p)

print("\n=== 2. 브랜드별 x 기종(GISONG) 호기 수 ===")
gisong_set = sorted(list(set(r['GISONG'] for r in rows if r['GISONG'])))
for b in [s['brand'] for s in brand_stats]:
    g_str = ", ".join([f"{g}: {len(brand_gisong[b][g])}개" for g in sorted(brand_gisong[b].keys(), key=lambda x: len(brand_gisong[b][x]), reverse=True)])
    print(f"- [{b}] Total: {len(brand_products[b])}개 -> {g_str}")

# 3. 브랜드별 속도(EL_ASPD) 분포
brand_aspd = defaultdict(lambda: defaultdict(set))
for r in rows:
    b = r['BRAND'] if r['BRAND'] else '기타/미정'
    spd = r['EL_ASPD'] if r['EL_ASPD'] else '미지정'
    p = r['PARENTNO']
    brand_aspd[b][spd].add(p)

print("\n=== 3. 브랜드별 x 속도대(EL_ASPD) 호기 수 ===")
for b in [s['brand'] for s in brand_stats]:
    spd_str = ", ".join([f"{spd}: {len(brand_aspd[b][spd])}개" for spd in sorted(brand_aspd[b].keys(), key=lambda x: len(brand_aspd[b][x]), reverse=True)])
    print(f"- [{b}] -> {spd_str}")

# 4. 세부 블록(BLOCKNO)별 분포
block_products = defaultdict(set)
block_bom_cnt = Counter()
for r in rows:
    blk = r['BLOCKNO'] if r['BLOCKNO'] else '기타/미지정'
    p = r['PARENTNO']
    block_products[blk].add(p)
    block_bom_cnt[blk] += 1

print("\n=== 4. 세부 블록(BLOCKNO)별 분포 ===")
for blk, prod_set in sorted(block_products.items(), key=lambda x: len(x[1]), reverse=True):
    print(f"- {blk}: {len(prod_set):,}개 호기 / {block_bom_cnt[blk]:,}건 BOM")

# 5. 주요 수배 자재 Top 10
part_products = defaultdict(set)
part_name_map = {}
for r in rows:
    pno = r['PARTNO']
    pname = r['PARTNAME']
    p = r['PARENTNO']
    part_products[pno].add(p)
    part_name_map[pno] = pname

print("\n=== 5. 최다 수배 자재 Top 10 ===")
for pno, prod_set in sorted(part_products.items(), key=lambda x: len(x[1]), reverse=True)[:10]:
    print(f"- {pno} ({part_name_map[pno]}): {len(prod_set):,}개 호기 (전체의 {len(prod_set)/total_distinct_products*100:.2f}%)")

# JSON 저장 (분석용)
results = {
    'total_bom_rows': total_bom_rows,
    'total_distinct_products': total_distinct_products,
    'brand_stats': brand_stats,
    'brand_gisong': {b: {g: len(ps) for g, ps in g_dict.items()} for b, g_dict in brand_gisong.items()},
    'brand_aspd': {b: {s: len(ps) for s, ps in spd_dict.items()} for b, spd_dict in brand_aspd.items()},
    'block_stats': [{'block': blk, 'prod_cnt': len(ps), 'bom_cnt': block_bom_cnt[blk]} for blk, ps in sorted(block_products.items(), key=lambda x: len(x[1]), reverse=True)],
    'top_parts': [{'part_no': pno, 'part_name': part_name_map[pno], 'prod_cnt': len(ps), 'ratio': round(len(ps)/total_distinct_products*100, 2)} for pno, ps in sorted(part_products.items(), key=lambda x: len(x[1]), reverse=True)[:10]]
}

with open("output_csv/a101a_stats_summary.json", "w", encoding="utf-8") as f:
    json.dump(results, f, ensure_ascii=False, indent=2)

print("\na101a_stats_summary.json 저장 완료.")
