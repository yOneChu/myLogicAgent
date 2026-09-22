import json
import re

def parse_con(con_str, val):
    """
    Evaluates if 'val' matches 'con_str'.
    CON notation 4 types:
      1. Single value ('KR00', '2500000731')
      2. List (',GTSS,GTLX,', 'GTSS,GTLX')
      3. Wildcard ('?GT?')
      4. Expression ('>1100', '<=2000')
      5. Negation ('!N', '!KR00') -> !N means not empty.
    """
    if con_str is None or str(con_str).strip() == "" or str(con_str).strip() == "-":
        # Empty CON
        return True, "Empty CON"
    
    con = str(con_str).strip()
    v = str(val).strip() if val is not None and str(val).strip() != "None" and str(val).strip() != "-" else ""

    # Negation !
    if con.startswith("!"):
        sub_con = con[1:]
        if sub_con == "N":
            res = (v != "")
            return res, f"Is Not Empty (!N): val='{v}' => {res}"
        else:
            match, msg = parse_con(sub_con, v)
            return not match, f"Not ({sub_con}): val='{v}' => {not match}"

    # Expression >, <, >=, <=
    m_exp = re.match(r"^([><]=?)(-?\d+(?:\.\d+)?)$", con)
    if m_exp:
        op, target_num = m_exp.groups()
        try:
            val_num = float(v)
            target_num = float(target_num)
            if op == ">": res = val_num > target_num
            elif op == ">=": res = val_num >= target_num
            elif op == "<": res = val_num < target_num
            elif op == "<=": res = val_num <= target_num
            return res, f"Numeric compare ({v} {op} {target_num}) => {res}"
        except ValueError:
            return False, f"Numeric compare error: val='{v}' not a number"

    # List check (e.g. ,GTSS,GTLX, or GTSS,GTLX)
    if "," in con:
        items = [x.strip() for x in con.split(",") if x.strip()]
        res = v in items or any(v == item for item in items)
        return res, f"List check ({v} in {items}) => {res}"

    # Wildcard ?
    if "?" in con or "*" in con:
        pattern = "^" + con.replace("?", ".").replace("*", ".*") + "$"
        res = bool(re.match(pattern, v))
        return res, f"Wildcard match ({v} against {con}) => {res}"

    # Exact single value match
    res = (v == con)
    return res, f"Exact match ('{v}' == '{con}') => {res}"

def evaluate_row(row, spec_map):
    reasons = []
    all_matched = True
    
    for i in range(1, 31):
        spec = row.get(f"SPEC{i}")
        con = row.get(f"CON{i}")
        
        if not spec or str(spec).strip() == "-" or str(spec).strip() == "":
            continue
            
        spec = str(spec).strip()
        val = spec_map.get(spec, "")
        
        matched, msg = parse_con(con, val)
        reasons.append(f"SPEC{i}({spec}): val='{val}', CON='{con}' -> {msg}")
        if not matched:
            all_matched = False
            
    return all_matched, reasons

def main():
    with open('output_csv/pid_EL_PB128A01_rows.json', 'r', encoding='utf-8') as f:
        rows = json.load(f)
        
    with open('output_csv/hogi_213249L36_spec_values.json', 'r', encoding='utf-8') as f:
        spec_values_raw = json.load(f)
        
    spec_map = {k: str(v['raw']) for k, v in spec_values_raw.items()}
    
    print(f"Total Rows: {len(rows)}")
    
    # Trace execution starting at ADDR 'MAIN'
    current_addr = "MAIN"
    addr_map = {}
    for r in rows:
        a = str(r.get("ADDR", "-")).strip()
        if a != "-":
            addr_map.setdefault(a, []).append(r)

    print("\n--- Executing Trace ---")
    
    idx = 0
    while idx < len(rows):
        row = rows[idx]
        no = row.get("NO")
        addr = str(row.get("ADDR", "-")).strip()
        goto = str(row.get("GOTO", "-")).strip()
        remarks = str(row.get("REMARKS", "-")).strip()
        
        # Check keys / vals
        keys_vals = []
        for k_idx in range(1, 21):
            k = row.get(f"KEY{k_idx}")
            v = row.get(f"VAL{k_idx}")
            if k and str(k).strip() != "-":
                keys_vals.append(f"KEY{k_idx}={k}, VAL{k_idx}={v}")

        matched, reasons = evaluate_row(row, spec_map)
        
        print(f"\n[Row NO.{no}] ADDR='{addr}', GOTO='{goto}', REMARKS='{remarks}' -> Matched: {matched}")
        if reasons:
            for r_msg in reasons:
                print(f"   - {r_msg}")
        if keys_vals:
            print(f"   => Outputs: {', '.join(keys_vals)}")

        if matched:
            if goto == "STOP":
                print(f"*** STOP reached at NO.{no}! Logic execution terminated. ***")
                break
            elif goto != "-" and goto != "":
                print(f"--> GOTO '{goto}' triggered at NO.{no}!")
                # Find index of first row with ADDR == goto
                found = False
                for search_idx, search_row in enumerate(rows):
                    if str(search_row.get("ADDR", "-")).strip() == goto:
                        idx = search_idx
                        found = True
                        break
                if not found:
                    print(f"Error: ADDR '{goto}' not found!")
                    break
                continue

        idx += 1

if __name__ == '__main__':
    main()
