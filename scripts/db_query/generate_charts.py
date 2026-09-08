import os
import matplotlib.pyplot as plt
from pathlib import Path

# 한글 폰트 설정 (Windows 맑은 고딕)
plt.rcParams['font.family'] = 'Malgun Gothic'
plt.rcParams['axes.unicode_minus'] = False

# 출력 디렉토리 생성
img_dir = Path("images")
img_dir.mkdir(parents=True, exist_ok=True)

# 1. 브랜드별 데이터
brands = ['NEX_MR', 'LUXEN_2', 'NEX_MRL', 'NEWYZER', 'NOBRAND', 'LUXEN_1', 'IXEL', '기타/미지정']
counts = [4090, 2200, 2012, 1052, 1050, 595, 277, 222]
colors = ['#2b5c8f', '#3690c0', '#67a9cf', '#a6bddb', '#d0d1e6', '#ece7f2', '#fff7bc', '#fee0d2']

# Chart 1: 브랜드별 점유율 파이 차트 (Pie Chart)
plt.figure(figsize=(9, 7), dpi=150)
wedges, texts, autotexts = plt.pie(
    counts,
    labels=brands,
    autopct='%1.1f%%',
    startangle=140,
    colors=colors,
    pctdistance=0.75,
    textprops={'fontsize': 11, 'weight': 'bold'}
)
plt.title('2026년 B181B 블록 브랜드별 점유율 (%)', fontsize=16, pad=20, weight='bold')
plt.tight_layout()
pie_chart_path = img_dir / "b181b_brand_pie_chart.png"
plt.savefig(pie_chart_path)
plt.close()

# Chart 2: 브랜드별 적용 현황 막대 차트 (Bar Chart)
plt.figure(figsize=(10, 6), dpi=150)
bars = plt.barh(brands[::-1], counts[::-1], color='#2b5c8f', edgecolor='black', alpha=0.85)

for bar in bars:
    width = bar.get_width()
    plt.text(width + 50, bar.get_y() + bar.get_height()/2, f'{width:,}건', 
             va='center', ha='left', fontsize=10, weight='bold')

plt.title('2026년 B181B 브랜드별 적용 현장 수 (건)', fontsize=16, pad=15, weight='bold')
plt.xlabel('적용 현장 수 (호기)', fontsize=12)
plt.xlim(0, 4700)
plt.grid(axis='x', linestyle='--', alpha=0.5)
plt.tight_layout()
bar_chart_path = img_dir / "b181b_brand_bar_chart.png"
plt.savefig(bar_chart_path)
plt.close()

print(f"Pie chart saved to: {pie_chart_path.resolve()}")
print(f"Bar chart saved to: {bar_chart_path.resolve()}")
