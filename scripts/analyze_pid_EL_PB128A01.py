import json
import ssl
import sys
import os
import csv
from urllib.parse import urlencode
from urllib.request import Request, urlopen

API_BASE_URL = "https://vault-in.hdel.co.kr:8070/api"
API_KEY = "subae"

def fetch_json(endpoint: str, params: dict = None, insecure: bool = True) -> any:
    if params is None:
        params = {}
    params["key"] = API_KEY
    url = f"{API_BASE_URL}/{endpoint}?{urlencode(params)}"
    
    req = Request(
        url,
        method="GET",
        headers={
            "Accept": "application/json",
            "User-Agent": "pid-analyzer/1.0",
        },
    )
    
    context = ssl._create_unverified_context() if insecure else None
    
    with urlopen(req, timeout=120, context=context) as response:
        raw_body = response.read()
        
    try:
        body = raw_body.decode("utf-8")
    except UnicodeDecodeError:
        body = raw_body.decode("cp949", errors="replace")
        
    return json.loads(body)

def main():
    pid = "EL_PB128A01"
    hogi = "213249L36"

    # 1. Fetch PID logic details
    sql_pid = f"""
    SELECT H.PID, H.VERSION, D.NO, NVL(D.ADDR, '-') AS ADDR, NVL(D.GOTO, '-') AS GOTO, NVL(D.REMARKS, '-') AS REMARKS,
           D.SPEC1, D.CON1, D.SPEC2, D.CON2, D.SPEC3, D.CON3, D.SPEC4, D.CON4, D.SPEC5, D.CON5,
           D.SPEC6, D.CON6, D.SPEC7, D.CON7, D.SPEC8, D.CON8, D.SPEC9, D.CON9, D.SPEC10, D.CON10,
           D.SPEC11, D.CON11, D.SPEC12, D.CON12, D.SPEC13, D.CON13, D.SPEC14, D.CON14, D.SPEC15, D.CON15,
           D.SPEC16, D.CON16, D.SPEC17, D.CON17, D.SPEC18, D.CON18, D.SPEC19, D.CON19, D.SPEC20, D.CON20,
           D.KEY1, D.VAL1, D.KEY2, D.VAL2, D.KEY3, D.VAL3, D.KEY4, D.VAL4, D.KEY5, D.VAL5
    FROM HDEL_DEFAULT.VARIANT_D D, HDEL_DEFAULT.VARIANT_H H, HDEL_DEFAULT.VARIANT_ID ID
    WHERE H.HOUID = ID.LAST_HOUID 
      AND H.HOUID = D.HOUID 
      AND H.PID = '{pid}'
    ORDER BY TO_NUMBER(D.NO)
    """

    print(f"Fetching PID logic for {pid}...")
    pid_res = fetch_json("executeQuery", {"sql": sql_pid})
    print(f"Retrieved {len(pid_res)} logic rows for {pid}.")

    # Collect all unique SPEC codes referenced in PID logic
    specs_needed = set()
    for row in pid_res:
        for i in range(1, 21):
            s = row.get(f"SPEC{i}")
            if s and s.strip() and s.strip() != "-":
                specs_needed.add(s.strip())

    print(f"Unique SPEC codes in {pid}: {sorted(list(specs_needed))}")

    # 2. Fetch Sales Specs for 213249L36
    sql_sales = f"""
    SELECT V.*
    FROM HDEL_DEFAULT.ELV_INFO$VF V,
         HDEL_DEFAULT.ELV_INFO$ID A
    WHERE V.vf$identity = A.id$ouid
      AND V.vf$ouid = A.id$wip
      AND V.MD$NUMBER = '{hogi}'
    """
    
    # Also fetch decoded sales spec values if any
    sql_sales_dec = f"""
    SELECT 
        V.MD$NUMBER AS PRODUCTNO,
        HDEL_DEFAULT.COD(V.EL_AOPEN) AS EL_AOPEN_DEC,
        HDEL_DEFAULT.CODN(V.EL_AUSE) AS EL_AUSE_DEC,
        HDEL_DEFAULT.CODN(V.EL_ABRAND) AS EL_ABRAND_DEC,
        HDEL_DEFAULT.CODN(V.EL_ATYP) AS EL_ATYP_DEC,
        HDEL_DEFAULT.CODN(V.EL_ASPD) AS EL_ASPD_DEC,
        HDEL_DEFAULT.CODN(V.EL_ACAPA) AS EL_ACAPA_DEC,
        HDEL_DEFAULT.COD(V.EL_ECWRL) AS EL_ECWRL_DEC,
        HDEL_DEFAULT.COD(V.EL_ETM) AS EL_ETM_DEC,
        HDEL_DEFAULT.COD(V.EL_ECSF) AS EL_ECSF_DEC,
        HDEL_DEFAULT.COD(V.EL_ASPC) AS EL_ASPC_DEC,
        HDEL_DEFAULT.COD(V.EL_ASPCD) AS EL_ASPCD_DEC,
        HDEL_DEFAULT.COD(V.EL_BCL) AS EL_BCL_DEC,
        HDEL_DEFAULT.COD(V.EL_DCRG) AS EL_DCRG_DEC,
        HDEL_DEFAULT.COD(V.EL_ASPSCD) AS EL_ASPSCD_DEC,
        HDEL_DEFAULT.COD(V.EL_ASPSC) AS EL_ASPSC_DEC,
        HDEL_DEFAULT.COD(V.EL_BCDM) AS EL_BCDM_DEC,
        HDEL_DEFAULT.COD(V.EL_BWALLT) AS EL_BWALLT_DEC,
        HDEL_DEFAULT.COD(V.EL_BCLCDL) AS EL_BCLCDL_DEC,
        HDEL_DEFAULT.COD(V.EL_BMOPB) AS EL_BMOPB_DEC,
        HDEL_DEFAULT.COD(V.EL_BETM) AS EL_BETM_DEC,
        HDEL_DEFAULT.COD(V.EL_BOPBSWD) AS EL_BOPBSWD_DEC
    FROM HDEL_DEFAULT.ELV_INFO$VF V,
         HDEL_DEFAULT.ELV_INFO$ID A
    WHERE V.vf$identity = A.id$ouid
      AND V.vf$ouid = A.id$wip
      AND V.MD$NUMBER = '{hogi}'
    """

    print(f"Fetching sales specs for {hogi}...")
    sales_res = fetch_json("executeQuery", {"sql": sql_sales})
    sales_dec_res = fetch_json("executeQuery", {"sql": sql_sales_dec})

    sales_data = sales_res[0] if sales_res else {}
    sales_dec_data = sales_dec_res[0] if sales_dec_res else {}

    # Print sales spec values relevant to PID
    print(f"\n--- Sales Spec Values for {hogi} ---")
    spec_values = {}
    for spec in sorted(list(specs_needed)):
        val = sales_data.get(spec, sales_data.get(spec.upper()))
        dec_val = sales_dec_data.get(f"{spec}_DEC", sales_dec_data.get(f"{spec.upper()}_DEC", ""))
        spec_values[spec] = {"raw": val, "dec": dec_val}
        print(f"  {spec}: raw='{val}', dec='{dec_val}'")

    os.makedirs('output_csv', exist_ok=True)
    with open('output_csv/pid_EL_PB128A01_rows.json', 'w', encoding='utf-8') as f:
        json.dump(pid_res, f, ensure_ascii=False, indent=2)

    with open('output_csv/hogi_213249L36_spec_values.json', 'w', encoding='utf-8') as f:
        json.dump(spec_values, f, ensure_ascii=False, indent=2)

if __name__ == '__main__':
    main()
