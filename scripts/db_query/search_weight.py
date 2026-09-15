# -*- coding: utf-8 -*-
"""
BLOCKNO$SF 및 PARTOFEBOM / NORMALPART$VF 에서 BALANCE / WEIGHT / CWT / 웨이트 관련 검색
"""

import json
from urllib.parse import urlencode
from urllib.request import Request, urlopen
import ssl

API_URL = "https://vault-in.hdel.co.kr:8070/api/executeQuery"
API_KEY = "subae"

def run_query(sql: str):
    query_string = urlencode({"key": API_KEY, "sql": sql})
    url = f"{API_URL}?{query_string}"
    req = Request(url, headers={"Accept": "application/json", "User-Agent": "Mozilla/5.0"})
    context = ssl._create_unverified_context()
    with urlopen(req, timeout=120, context=context) as resp:
        return json.loads(resp.read().decode("utf-8", errors="replace"))

# 1. BLOCKNO$SF 컬럼 조회
print("--- BLOCKNO$SF Sample ---")
res_block_sample = run_query("SELECT * FROM BLOCKNO$SF WHERE ROWNUM <= 5")
print(json.dumps(res_block_sample, ensure_ascii=False, indent=2))

# 2. BLOCKNO$SF 에서 WEIGHT / CWT / BALANCE / 웨이트 검색
print("--- BLOCKNO$SF search WEIGHT / CWT / BALANCE ---")
res_block_weight = run_query("SELECT MD$NUMBER, BLOCK_OPT FROM BLOCKNO$SF WHERE UPPER(MD$NUMBER) LIKE '%WT%' OR UPPER(BLOCK_OPT) LIKE '%WEIGHT%' OR UPPER(BLOCK_OPT) LIKE '%BALAN%' OR UPPER(BLOCK_OPT) LIKE '%CWT%' OR UPPER(BLOCK_OPT) LIKE '%웨이트%' ROWNUM <= 30")
print(json.dumps(res_block_weight, ensure_ascii=False, indent=2))

# 3. NORMALPART$VF 에서 벨런스웨이트 / 밸런스웨이트 / BALANCE WEIGHT / B120 검색
print("--- NORMALPART$VF search WEIGHT ---")
res_part_weight = run_query("SELECT MD$NUMBER, MD$DESC, SPEC FROM NORMALPART$VF WHERE UPPER(MD$DESC) LIKE '%밸런스%' OR UPPER(MD$DESC) LIKE '%벨런스%' OR UPPER(MD$DESC) LIKE '%BALANCE%WEIGHT%' OR UPPER(MD$DESC) LIKE '%COUNTER%WEIGHT%' ROWNUM <= 30")
print(json.dumps(res_part_weight, ensure_ascii=False, indent=2))

# 4. PARTOFEBOM 의 CMT 나 SPEC 에서 B120B03 검색
print("--- PARTOFEBOM search CMT / SPEC for B120B03 ---")
res_pe = run_query("SELECT PE.PRODUCTOUID, PE.CMT, NP.MD$NUMBER, NP.MD$DESC, NP.SPEC FROM PARTOFEBOM PE INNER JOIN NORMALPART$VF NP ON PE.PARTOUID = NP.VF$OUID WHERE UPPER(PE.CMT) LIKE '%B120B03%' OR UPPER(NP.SPEC) LIKE '%B120B03%' ROWNUM <= 20")
print(json.dumps(res_pe, ensure_ascii=False, indent=2))

