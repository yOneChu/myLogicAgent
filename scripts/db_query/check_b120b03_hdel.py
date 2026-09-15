# -*- coding: utf-8 -*-
"""
HDEL_DEFAULT.BLOCKNO$SF 및 HDEL_DEFAULT.NORMALPART$VF 에서 B120B03 검색
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

# 1. HDEL_DEFAULT.BLOCKNO$SF 에서 B120B03 검색
print("--- 1. HDEL_DEFAULT.BLOCKNO$SF for B120B03 ---")
sql1 = "SELECT MD$NUMBER, SF$OUID, BLOCK_OPT FROM HDEL_DEFAULT.BLOCKNO$SF WHERE UPPER(MD$NUMBER) LIKE '%B120B03%'"
res1 = run_query(sql1)
print(json.dumps(res1, ensure_ascii=False, indent=2))

# 2. HDEL_DEFAULT.BLOCKNO$SF 에서 B120B% 검색
print("--- 2. HDEL_DEFAULT.BLOCKNO$SF for B120B% ---")
sql2 = "SELECT MD$NUMBER, SF$OUID, BLOCK_OPT FROM HDEL_DEFAULT.BLOCKNO$SF WHERE UPPER(MD$NUMBER) LIKE 'B120B%'"
res2 = run_query(sql2)
print(json.dumps(res2, ensure_ascii=False, indent=2))

# 3. HDEL_DEFAULT.NORMALPART$VF 에서 B120B03 검색
print("--- 3. HDEL_DEFAULT.NORMALPART$VF for B120B03 ---")
sql3 = "SELECT MD$NUMBER, MD$DESC, SPEC, BLOCKNO FROM HDEL_DEFAULT.NORMALPART$VF WHERE UPPER(MD$NUMBER) LIKE '%B120B03%' OR UPPER(SPEC) LIKE '%B120B03%' OR UPPER(MD$DESC) LIKE '%B120B03%'"
res3 = run_query(sql3)
print(json.dumps(res3, ensure_ascii=False, indent=2))
