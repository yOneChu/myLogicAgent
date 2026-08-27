import csv
from collections import defaultdict
import sys
import io

# Windows 콘솔 출력 인코딩 설정
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

def verify_logic(csv_path: str):
    with open(csv_path, "r", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        rows = list(reader)

    print(f"==================================================")
    print(f"  PID EL_PB121B (테스트 버전 VERSION=-1) 로직 검증  ")
    print(f"==================================================\n")
    print(f"총 검증 대상 행(Row) 수: {len(rows)}건\n")

    # 1. SPEC / CON 문법 오류 및 [확인 필요] 검사
    spec_con_errors = []
    spec_con_check_needed = []

    for row in rows:
        no = row.get("NO", "")
        addr = row.get("ADDR", "-")
        remarks = row.get("REMARKS", "-")

        for i in range(1, 31):
            s_val = row.get(f"SPEC{i}", "").strip()
            c_val = row.get(f"CON{i}", "").strip()

            s_is_empty = (s_val == "" or s_val == "-")
            c_is_empty = (c_val == "" or c_val == "-")

            # 1) SPEC이 공백인데 CON에 값이 있으면 오류
            if s_is_empty and not c_is_empty:
                spec_con_errors.append({
                    "NO": no,
                    "ADDR": addr,
                    "PAIR": f"SPEC{i}/CON{i}",
                    "SPEC": s_val,
                    "CON": c_val,
                    "REMARKS": remarks
                })

            # 2) SPEC만 있고 CON이 빈 칸인 경우 [확인 필요]
            elif not s_is_empty and c_is_empty:
                spec_con_check_needed.append({
                    "NO": no,
                    "ADDR": addr,
                    "PAIR": f"SPEC{i}/CON{i}",
                    "SPEC": s_val,
                    "CON": c_val,
                    "REMARKS": remarks
                })

    # 2. ADDR, REMARKS 열 제외하고 나머지 SPEC + CON + KEY + VAL + GOTO 중복 행 검사
    key_map = defaultdict(list)
    for row in rows:
        no = row.get("NO", "")
        addr = row.get("ADDR", "-").strip()
        remarks = row.get("REMARKS", "-").strip()
        goto_val = row.get("GOTO", "-").strip()

        tuple_items = [("GOTO", goto_val)]

        for i in range(1, 31):
            s = row.get(f"SPEC{i}", "-").strip()
            c = row.get(f"CON{i}", "-").strip()
            tuple_items.append((f"SPEC{i}", s if s != "" else "-"))
            tuple_items.append((f"CON{i}", c if c != "" else "-"))

        for i in range(1, 21):
            k = row.get(f"KEY{i}", "-").strip()
            v = row.get(f"VAL{i}", "-").strip()
            tuple_items.append((f"KEY{i}", k if k != "" else "-"))
            tuple_items.append((f"VAL{i}", v if v != "" else "-"))

        combo_key = tuple(tuple_items)
        key_map[combo_key].append({
            "NO": no,
            "ADDR": addr,
            "REMARKS": remarks
        })

    duplicates = {k: v for k, v in key_map.items() if len(v) > 1}

    # 결과 리포트 출력
    print("--------------------------------------------------")
    print(" 1. SPEC / CON 문법 규칙 검사 결과")
    print("--------------------------------------------------")
    
    # 1-1) SPEC 공백, CON 값 존재 (오류)
    if not spec_con_errors:
        print("[정상] SPEC이 공백인데 CON에 값이 있는 오류 항목이 없습니다.")
    else:
        print(f"[오류] SPEC이 공백인데 CON에 값이 존재하는 항목: 총 {len(spec_con_errors)}건")
        for err in spec_con_errors:
            print(f"   - 라인 (NO) {err['NO']}: {err['PAIR']} (SPEC: '{err['SPEC']}', CON: '{err['CON']}') | ADDR: {err['ADDR']}, REMARKS: {err['REMARKS']}")

    print()
    # 1-2) SPEC만 있고 CON이 빈 칸인 경우 [확인 필요]
    if not spec_con_check_needed:
        print("[정상] SPEC만 있고 CON이 비어 있는 [확인 필요] 항목이 없습니다.")
    else:
        print(f"[확인 필요] SPEC만 있고 CON이 비어 있는 항목: 총 {len(spec_con_check_needed)}건")
        for item in spec_con_check_needed:
            print(f"   - 라인 (NO) {item['NO']}: {item['PAIR']} (SPEC: '{item['SPEC']}', CON: '{item['CON']}') | ADDR: {item['ADDR']}, REMARKS: {item['REMARKS']}")

    print("\n--------------------------------------------------")
    print(" 2. ADDR, REMARKS 제외 중복 행 검사 결과")
    print("--------------------------------------------------")

    if not duplicates:
        print("[정상] SPEC + CON + KEY + VAL + GOTO 조합이 동일한 중복 행이 없습니다.")
    else:
        valid_dup = []
        empty_dup = []

        for combo, item_list in duplicates.items():
            non_empty_specs = [(k, v) for k, v in combo if (k.startswith("SPEC") or k.startswith("CON")) and v != "-"]
            non_empty_keys = [(k, v) for k, v in combo if (k.startswith("KEY") or k.startswith("VAL")) and v != "-"]
            goto_item = [(k, v) for k, v in combo if k == "GOTO" and v != "-"]

            if not non_empty_specs and not non_empty_keys and not goto_item:
                empty_dup.append((combo, item_list))
            else:
                valid_dup.append((combo, item_list))

        print(f"[문법 위반] 중복된 행 그룹 총 {len(duplicates)}개 발견")
        print(f"   - 로직 조건/산출 중복 그룹: {len(valid_dup)}개")
        print(f"   - 완전히 비어있는 행(Empty Line) 중복 그룹: {len(empty_dup)}개\n")

        if valid_dup:
            print(" [상세 로직 중복 목록]")
            for idx, (combo, item_list) in enumerate(valid_dup, 1):
                lines = [item["NO"] for item in item_list]
                print(f"  그룹 {idx}) 중복 라인 (NO): {', '.join(lines)}")
                
                # 중복된 SPEC/CON/KEY/VAL/GOTO 내용 요약
                active_spec_con = []
                for i in range(1, 31):
                    s = dict(combo).get(f"SPEC{i}", "-")
                    c = dict(combo).get(f"CON{i}", "-")
                    if s != "-" or c != "-":
                        active_spec_con.append(f"{s}={c}")
                
                active_key_val = []
                for i in range(1, 21):
                    k = dict(combo).get(f"KEY{i}", "-")
                    v = dict(combo).get(f"VAL{i}", "-")
                    if k != "-" or v != "-":
                        active_key_val.append(f"{k}={v}")

                goto_str = dict(combo).get("GOTO", "-")

                if goto_str != "-":
                    print(f"      - GOTO: {goto_str}")
                if active_spec_con:
                    print(f"      - SPEC/CON: {', '.join(active_spec_con)}")
                if active_key_val:
                    print(f"      - KEY/VAL: {', '.join(active_key_val)}")

                for item in item_list:
                    print(f"      * 라인 {item['NO']}: ADDR='{item['ADDR']}', REMARKS='{item['REMARKS']}'")
                print()

        if empty_dup:
            print(" [완전히 비어있는 빈 행 중복 목록]")
            for idx, (combo, item_list) in enumerate(empty_dup, 1):
                lines = [item["NO"] for item in item_list]
                print(f"  빈 행 그룹 {idx}) 중복 라인 (NO): {', '.join(lines)}")
                for item in item_list:
                    print(f"      * 라인 {item['NO']}: ADDR='{item['ADDR']}', REMARKS='{item['REMARKS']}'")

if __name__ == "__main__":
    verify_logic("output_csv/el_pb121b_test.csv")
