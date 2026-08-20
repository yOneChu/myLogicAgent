import csv
from collections import defaultdict

def check_duplicates_detail(csv_path: str):
    with open(csv_path, "r", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        rows = list(reader)
    
    print(f"Total rows: {len(rows)}")
    
    key_map = defaultdict(list)
    
    for row in rows:
        no = row.get("NO", "")
        addr = row.get("ADDR", "-").strip()
        remarks = row.get("REMARKS", "-").strip()
        goto_val = row.get("GOTO", "-").strip()
        
        full_tuple_list = [("GOTO", goto_val)]
        for i in range(1, 31):
            full_tuple_list.append((f"SPEC{i}", row.get(f"SPEC{i}", "-").strip()))
            full_tuple_list.append((f"CON{i}", row.get(f"CON{i}", "-").strip()))
        for i in range(1, 21):
            full_tuple_list.append((f"KEY{i}", row.get(f"KEY{i}", "-").strip()))
            full_tuple_list.append((f"VAL{i}", row.get(f"VAL{i}", "-").strip()))
            
        combo_key = tuple(full_tuple_list)
        key_map[combo_key].append({
            "NO": no,
            "ADDR": addr,
            "REMARKS": remarks
        })

    duplicates = {k: v for k, v in key_map.items() if len(v) > 1}
    
    print(f"\n==========================================")
    print(f"       PICK_B121A 중복 라인 검사 결과      ")
    print(f"==========================================\n")
    
    if not duplicates:
        print("중복된 라인이 없습니다.")
    else:
        print(f"총 {len(duplicates)}개의 중복 그룹이 발견되었습니다.\n")
        for idx, (combo, item_list) in enumerate(duplicates.items(), 1):
            lines = [item["NO"] for item in item_list]
            
            # 의미있는 내용 정리
            non_empty_specs = [(k, v) for k, v in combo if (k.startswith("SPEC") or k.startswith("CON")) and v != "-"]
            non_empty_keys = [(k, v) for k, v in combo if (k.startswith("KEY") or k.startswith("VAL")) and v != "-"]
            goto_item = [(k, v) for k, v in combo if k == "GOTO" and v != "-"]
            
            is_completely_empty = (not non_empty_specs and not non_empty_keys and not goto_item)
            
            print(f"[중복 그룹 {idx}]")
            print(f" - 해당 라인 (NO): {', '.join(lines)} (총 {len(lines)}개 행)")
            if is_completely_empty:
                print(" - 유형: SPEC, CON, KEY, VAL, GOTO가 모두 비어있는 '빈 행(Empty Line)' 중복")
            else:
                print(" - 유형: 실제 조건/산출 로직 중복")
                print(f" - GOTO: {goto_item[0][1] if goto_item else '-'}")
                print(f" - SPEC/CON: {non_empty_specs}")
                print(f" - KEY/VAL: {non_empty_keys}")
            
            print(" - 세부 행 정보:")
            for item in item_list[:10]: # 최대 10개만 예시 출력
                print(f"    * 라인 {item['NO']}: ADDR='{item['ADDR']}', REMARKS='{item['REMARKS']}'")
            if len(item_list) > 10:
                print(f"    * ... 외 {len(item_list) - 10}개 생략")
            print("-" * 50)

if __name__ == "__main__":
    check_duplicates_detail("output_csv/pick_b121a_test.csv")
