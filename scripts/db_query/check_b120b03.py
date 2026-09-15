# -*- coding: utf-8 -*-
"""
B120B03 및 유사 키워드 검색 스크립트
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

# 1. BLOCKNO$SF 에서 120B03 or B120B or B120 검색
sql_block = "SELECT MD$NUMBER, SF$OUID, BLOCK_OPT FROM BLOCKNO$SF WHERE UPPER(MD$NUMBER) LIKE '%120B%'"
print("--- 1. BLOCKNO$SF LIKE '%120B%' ---")
res_block = run_query(sql_block)
print(json.dumps(res_block[:20], ensure_ascii=False, indent=2))

# 2. NORMALPART$VF 에서 120B03 or B120B 검색
sql_part = "SELECT MD$NUMBER, MD$DESC, SPEC FROM NORMALPART$VF WHERE UPPER(MD$NUMBER) LIKE '%120B03%' OR UPPER(SPEC) LIKE '%120B03%' OR UPPER(MD$DESC) LIKE '%120B03%' ROWNUM <= 20"
print("--- 2. NORMALPART$VF LIKE '%120B03%' ---")
res_part = run_query(sql_part)
print(json.dumps(res_part, ensure_ascii=False, indent=2))

# 3. BLOCKNO$SF 에서 B120 계열 검색
sql_block_b120 = "SELECT MD$NUMBER, SF$OUID, BLOCK_OPT FROM BLOCKNO$SF WHERE UPPER(MD$NUMBER) LIKE 'B120%' OR UPPER(MD$NUMBER) LIKE 'P120%'"
print("--- 3. BLOCKNO$SF LIKE 'B120%' OR 'P120%' ---")
res_block_b120 = run_query(sql_block_b120)
print(json.dumps(res_block_b120[:30], ensure_ascii=False, indent=2))

# 4. NORMALPART$VF 에서 BLOCKNO hex로 안거쳐도 spec이나 desc에 B120B03 비슷한게 있는지
sql_spec = "SELECT MD$NUMBER, MD$DESC, SPEC FROM NORMALPART$VF WHERE UPPER(SPEC) LIKE '%120B%' OR UPPER(MD$DESC) LIKE '%120B%' ROWNUM <= 20"
print("--- 4. SPEC or DESC LIKE '%120B%' ---")
res_spec = run_query(sql_spec)
print(json.dumps(res_spec, ensure_ascii=False, indent=2))
