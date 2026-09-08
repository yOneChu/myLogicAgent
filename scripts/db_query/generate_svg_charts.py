import math
from pathlib import Path

img_dir = Path("images")
img_dir.mkdir(parents=True, exist_ok=True)

# Data
brands = ['NEX_MR', 'LUXEN_2', 'NEX_MRL', 'NEWYZER', 'NOBRAND', 'LUXEN_1', 'IXEL', '기타/미지정']
counts = [4090, 2200, 2012, 1052, 1050, 595, 277, 222]
percentages = [35.57, 19.13, 17.50, 9.15, 9.13, 5.17, 2.41, 1.94]
colors = ['#2b5c8f', '#3690c0', '#67a9cf', '#a6bddb', '#8c6bb1', '#88419d', '#feb24c', '#fd8d3c']

# 1. Generate SVG Pie Chart
def create_pie_svg():
    total = sum(counts)
    cx, cy, r = 300, 250, 180
    
    svg = [
        '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 800 500" style="background-color: #ffffff;">',
        '<style>',
        '  .title { font-family: "Malgun Gothic", sans-serif; font-size: 22px; font-weight: bold; fill: #1a202c; }',
        '  .label { font-family: "Malgun Gothic", sans-serif; font-size: 14px; font-weight: bold; fill: #2d3748; }',
        '  .legend { font-family: "Malgun Gothic", sans-serif; font-size: 14px; fill: #4a5568; }',
        '</style>',
        '<text x="400" y="40" text-anchor="middle" class="title">2026년 B181B 블록 브랜드별 점유율 (%)</text>'
    ]
    
    start_angle = -90
    for i, (brand, count, pct, color) in enumerate(zip(brands, counts, percentages, colors)):
        angle = (count / total) * 360
        end_angle = start_angle + angle
        
        # Calculate SVG Arc coordinates
        x1 = cx + r * math.cos(math.radians(start_angle))
        y1 = cy + r * math.sin(math.radians(start_angle))
        x2 = cx + r * math.cos(math.radians(end_angle))
        y2 = cy + r * math.sin(math.radians(end_angle))
        
        large_arc = 1 if angle > 180 else 0
        path = f"M {cx} {cy} L {x1:.2f} {y1:.2f} A {r} {r} 0 {large_arc} 1 {x2:.2f} {y2:.2f} Z"
        
        svg.append(f'<path d="{path}" fill="{color}" stroke="#ffffff" stroke-width="2"/>')
        
        # Legend item
        lx = 540
        ly = 120 + i * 40
        svg.append(f'<rect x="{lx}" y="{ly}" width="20" height="20" rx="4" fill="{color}"/>')
        svg.append(f'<text x="{lx + 30}" y="{ly + 15}" class="legend">{brand}: {count:,}건 ({pct:.2f}%)</text>')
        
        start_angle = end_angle

    svg.append('</svg>')
    return '\n'.join(svg)

# 2. Generate SVG Bar Chart
def create_bar_svg():
    max_val = max(counts)
    chart_w, chart_h = 500, 320
    start_x, start_y = 180, 80
    
    svg = [
        '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 800 480" style="background-color: #ffffff;">',
        '<style>',
        '  .title { font-family: "Malgun Gothic", sans-serif; font-size: 22px; font-weight: bold; fill: #1a202c; }',
        '  .axis-label { font-family: "Malgun Gothic", sans-serif; font-size: 14px; font-weight: bold; fill: #2d3748; }',
        '  .bar-val { font-family: "Malgun Gothic", sans-serif; font-size: 13px; font-weight: bold; fill: #1a202c; }',
        '</style>',
        '<text x="400" y="40" text-anchor="middle" class="title">2026년 B181B 브랜드별 적용 현장 수 (건)</text>'
    ]
    
    bar_height = 28
    gap = 12
    
    for i, (brand, count, color) in enumerate(zip(brands, counts, colors)):
        y = start_y + i * (bar_height + gap)
        w = (count / max_val) * chart_w
        
        # Brand Name Label
        svg.append(f'<text x="{start_x - 15}" y="{y + 19}" text-anchor="end" class="axis-label">{brand}</text>')
        # Bar rect
        svg.append(f'<rect x="{start_x}" y="{y}" width="{w:.2f}" height="{bar_height}" rx="4" fill="{color}"/>')
        # Value text
        svg.append(f'<text x="{start_x + w + 10}" y="{y + 19}" class="bar-val">{count:,}건</text>')
        
    svg.append('</svg>')
    return '\n'.join(svg)

# Write SVG files
pie_svg_path = img_dir / "b181b_brand_pie_chart.svg"
bar_svg_path = img_dir / "b181b_brand_bar_chart.svg"

pie_svg_path.write_text(create_pie_svg(), encoding='utf-8')
bar_svg_path.write_text(create_bar_svg(), encoding='utf-8')

print("Pie SVG created:", pie_svg_path.resolve())
print("Bar SVG created:", bar_svg_path.resolve())
