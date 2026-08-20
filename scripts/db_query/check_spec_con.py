import csv
from collections import defaultdict

def check_spec_con_duplicates(csv_path: str):
    with open(csv_path, "r", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        rows = list(reader)
    
    print(f"Total rows: {len(rows)}")
    
    key_map = defaultdict(list)
    
    for row in rows:
        no = row.get("NO", "")
        addr = row.get("ADDR", "-").strip()
        remarks = row.get("REMARKS", "-").strip()
        
        # SPEC 1~30, CON 1~30 튜플 생성
        spec_con_list = []
        for i in range(1, 31):
            s = row.get(f"SPEC{i}", "-").strip()
            c = row.get(f"CON{i}", "-").strip()
            spec_con_list.append((f"SPEC{i}", s))
            spec_con_list.append((f"CON{i}", c))
            
        combo_key = tuple(spec_con_list)
        key_map[combo_key].append({
            "NO": no,
            "ADDR": addr,
            "REMARKS": remarks
        })

    duplicates = {k: v for k, v in key_map.items() if len(v) > 1}
    
    print(f"\n==========================================")
    print(f"   PICK_B121A SPEC+CON 조합 중복 검사 결과  ")
    print(f"==========================================\n")
    
    if not duplicates:
        print("SPEC + CON 조합으로 중복된 라인이 없습니다.")
    else:
        valid_dup_count = 0
        empty_dup_count = 0
        
        for idx, (combo, item_list) in enumerate(duplicates.items(), 1):
            lines = [item["NO"] for item in item_list]
            
            # 의미있는 SPEC/CON 값 추출
            non_empty_specs = [(k, v) for k, v in combo if v != "-"]
            
            if not non_empty_specs:
                empty_dup_count += 1
            else:
                valid_dup_count += 1
                
        print(f"총 {len(duplicates)}개 그룹의 SPEC+CON 중복이 발견되었습니다.")
        print(f" - 유효한 SPEC+CON 조건 중복: {valid_dup_count}개 그룹")
        print(f" - 빈 SPEC+CON (조건 없음) 중복: {empty_dup_count}개 그룹\n")
        print("="*60 + "\n")
        
        group_no = 1
        for combo, item_list in duplicates.items():
            lines = [item["NO"] for item in item_list]
            non_empty_specs = [(k, v) for k, v in combo if v != "-"]
            
            if non_empty_specs:
                print(f"[유효 조건 중복 그룹 {group_no}]")
                print(f" - 해당 라인 (NO): {', '.join(lines)} (총 {len(lines)}개 행)")
                print(f" - SPEC + CON 조건 내용:")
                # SPEC과 CON을 보기 좋게 쌍으로 묶어서 표시
                spec_pairs = []
                for i in range(1, 31):
                    s = dict(combo).get(f"SPEC{i}", "-")
                    c = dict(combo).get(f"CON{i}", "-")
                    if s != "-" or c != "-":
                        spec_pairs.append(f"{s} = {c}")
                print(f"    * {', '.join(spec_pairs)}")
                
                print(" - 세부 행 정보 (NO / ADDR / REMARKS):")
                for item in item_list:
                    print(f"    * 라인 {item['NO']}: ADDR='{item['ADDR']}', REMARKS='{item['REMARKS']}'")
                print("-" * 60 + "\n")
                group_no += 1
        
        if empty_dup_count > 0:
            for combo, item_list in duplicates.items():
                non_empty_specs = [(k, v) for k, v in combo if v != "-"]
                if not non_empty_specs:
                    lines = [item["NO"] for item in item_list]
                    print(f"[빈 SPEC+CON 조건 그룹]")
                    print(f" - 해당 라인 (NO): {', '.join(lines)} (총 {len(lines)}개 행)")
                    print(" - 유형: SPEC1~30, CON1~30 조건이 모두 비어있는 행들")
                    print("-" * 60 + "\n")

if __name__ == "__main__":
    check_spec_con_duplicates("output_csv/pick_b121a_test.csv")
