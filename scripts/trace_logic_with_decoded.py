import json

def main():
    with open('output_csv/pid_EL_PB128A01_rows.json', 'r', encoding='utf-8') as f:
        rows = json.load(f)
        
    with open('output_csv/hogi_213249L36_spec_values.json', 'r', encoding='utf-8') as f:
        spec_values_raw = json.load(f)
        
    # Use decoded value if present, else fallback to raw
    spec_map_decoded = {}
    for k, v in spec_values_raw.items():
        dec = str(v['dec']).strip()
        raw = str(v['raw']).strip()
        # Clean decoded value (e.g. "N:EX_MRL (헤월)" -> "NEX_MRL" or "N:EX_MRL", "45m/m (0.75m/s)" -> "45")
        if dec and dec != "None":
            # Extract main code if formatted like "N:EX_MRL (헤월...)" -> NEX_MRL or N:EX_MRL
            if "(" in dec:
                dec_clean = dec.split("(")[0].strip()
            else:
                dec_clean = dec
            # remove N: if needed or test both
            spec_map_decoded[k] = dec_clean
        else:
            spec_map_decoded[k] = raw

    from trace_logic_EL_PB128A01 import evaluate_row

    print("=== Execution Trace with Decoded Spec Values ===")
    print("Decoded Spec Map:", spec_map_decoded)
    
    idx = 0
    while idx < len(rows):
        row = rows[idx]
        no = str(row.get("NO"))
        addr = str(row.get("ADDR", "-")).strip()
        goto = str(row.get("GOTO", "-")).strip()
        remarks = str(row.get("REMARKS", "-")).strip()
        
        matched, reasons = evaluate_row(row, spec_map_decoded)
        
        outputs = []
        for k_idx in range(1, 21):
            k = row.get(f"KEY{k_idx}")
            v = row.get(f"VAL{k_idx}")
            if k and str(k).strip() != "-":
                outputs.append(f"{k}={v}")
                
        out_str = f" | Outputs: {', '.join(outputs)}" if outputs else ""
        
        if matched or (addr != '-' or goto != '-'):
            status = "MATCHED" if matched else "SKIPPED"
            print(f"Row {no:>3s} | ADDR: {addr:12s} | GOTO: {goto:10s} | Status: {status:7s}{out_str} | Remarks: {remarks}")
            if not matched:
                for r in reasons:
                    if "False" in r:
                        print(f"   --> {r}")

        if matched:
            if goto == "STOP":
                print(f"\n[STOP] Reached STOP at Row {no}. Terminating PID execution.")
                break
            elif goto != "-" and goto != "":
                print(f"\n[GOTO] Jumping to ADDR '{goto}' from Row {no}...")
                found = False
                for s_idx, s_row in enumerate(rows):
                    if str(s_row.get("ADDR", "-")).strip() == goto:
                        idx = s_idx
                        found = True
                        break
                if not found:
                    print(f"ERROR: Target ADDR '{goto}' not found.")
                    break
                continue
        idx += 1

if __name__ == '__main__':
    main()
