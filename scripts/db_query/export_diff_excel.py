import json
import os
import csv

os.makedirs("output_excel", exist_ok=True)
os.makedirs("output_csv", exist_ok=True)

with open("output_csv/EL_PA103A03_v44_v45_korean_diff.json", "r", encoding="utf-8") as f:
    diff_data = json.load(f)

excel_rows = []

for item in diff_data:
    no = item["NO"]
    t = item["TYPE"]
    
    if t == "MODIFIED":
        v44_row = item.get("v44_row", {})
        v45_row = item.get("v45_row", {})
        changed_fields = list(item.get("field_diffs", {}).keys())
        
        detail_list = []
        for fld, vals in item.get("field_diffs", {}).items():
            detail_list.append(f"{fld}: [{vals['v44']}] -> [{vals['v45']}]")
            
        excel_rows.append({
            "NO": no,
            "구분": "수정(MODIFIED)",
            "주요 변경 필드": ", ".join(changed_fields),
            "v44 정보": item.get("v44_summary"),
            "v45 정보": item.get("v45_summary"),
            "상세 변경 내용": " | ".join(detail_list)
        })
    elif t == "ADDED_IN_V45":
        excel_rows.append({
            "NO": no,
            "구분": "v45 신규 추가",
            "주요 변경 필드": "전체 행 추가",
            "v44 정보": "-",
            "v45 정보": item.get("v45_summary"),
            "상세 변경 내용": "v45 버전에서 신규 추가된 행"
        })
    elif t == "DELETED_IN_V45":
        excel_rows.append({
            "NO": no,
            "구분": "v45 삭제",
            "주요 변경 필드": "전체 행 삭제",
            "v44 정보": item.get("v44_summary"),
            "v45 정보": "-",
            "상세 변경 내용": "v45 버전에서 삭제된 행"
        })

fieldnames = ["NO", "구분", "주요 변경 필드", "v44 정보", "v45 정보", "상세 변경 내용"]
csv_path = "output_csv/EL_PA103A03_v44_v45_diff_report.csv"

with open(csv_path, "w", newline="", encoding="utf-8-sig") as f:
    writer = csv.DictWriter(f, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows(excel_rows)

print(f"CSV report successfully generated at: {csv_path}")
