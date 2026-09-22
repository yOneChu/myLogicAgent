import json

def main():
    with open('output_csv/pid_EL_PB128A01_rows.json', 'r', encoding='utf-8') as f:
        rows = json.load(f)
        
    with open('output_csv/hogi_213249L36_spec_values.json', 'r', encoding='utf-8') as f:
        spec_values_raw = json.load(f)
        
    spec_map = {k: str(v['raw']) for k, v in spec_values_raw.items()}

    from trace_logic_EL_PB128A01 import evaluate_row

    logs = []
    logs.append("=== Detailed Execution Trace for PID EL_PB128A01 (HOGI: 213249L36) ===")
    
    idx = 0
    matched_rows = []
    
    while idx < len(rows):
        row = rows[idx]
        no = str(row.get("NO"))
        addr = str(row.get("ADDR", "-")).strip()
        goto = str(row.get("GOTO", "-")).strip()
        remarks = str(row.get("REMARKS", "-")).strip()
        
        matched, reasons = evaluate_row(row, spec_map)
        
        status = "MATCHED" if matched else "SKIPPED"
        outputs = []
        for k_idx in range(1, 21):
            k = row.get(f"KEY{k_idx}")
            v = row.get(f"VAL{k_idx}")
            if k and str(k).strip() != "-":
                outputs.append(f"{k}={v}")
                
        out_str = f" | Outputs: {', '.join(outputs)}" if outputs else ""
        
        logs.append(f"Row {no:>3s} | ADDR: {addr:12s} | GOTO: {goto:10s} | Status: {status:7s}{out_str} | Remarks: {remarks}")
        if not matched and (addr != '-' or goto != '-'):
            logs.append(f"   --> Mismatch Reason: {reasons[0] if reasons else 'N/A'}")
        elif not matched:
            for r_msg in reasons:
                if "False" in r_msg:
                    logs.append(f"   --> Mismatch Reason: {r_msg}")

        if matched:
            matched_rows.append(row)
            if goto == "STOP":
                logs.append(f"\n[STOP] Reached STOP at Row {no}. Terminating PID execution.")
                break
            elif goto != "-" and goto != "":
                logs.append(f"\n[GOTO] Jumping to ADDR '{goto}' from Row {no}...")
                found = False
                for s_idx, s_row in enumerate(rows):
                    if str(s_row.get("ADDR", "-")).strip() == goto:
                        idx = s_idx
                        found = True
                        break
                if not found:
                    logs.append(f"ERROR: Target ADDR '{goto}' not found.")
                    break
                continue
        idx += 1

    with open('output_csv/pid_trace_full.txt', 'w', encoding='utf-8') as f:
        f.write("\n".join(logs))

    print("Trace log written to output_csv/pid_trace_full.txt")

if __name__ == '__main__':
    main()
