# -*- coding: utf-8 -*-
"""
B120B03 관련 자재 및 호기 조건 단계별 검증 스크립트
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

# 1. B120B03 블록에 속한 자재 개수 및 샘플
sql1 = """
SELECT NP.VF$OUID, NP.MD$NUMBER, NP.MD$DESC, NP.SPEC, NP.BLOCKNO 
  FROM HDEL_DEFAULT.NORMALPART$VF NP
 WHERE (SELECT MD$NUMBER FROM HDEL_DEFAULT.BLOCKNO$SF 
         WHERE SF$OUID = DECODE(NP.BLOCKNO, NULL, NULL, HDEL_DEFAULT.HEXTODEC(UPPER(SUBSTR(NP.BLOCKNO, 12))))) = 'B120B03'
"""
print("--- 1. B120B03 자재 목록 ---")
res1 = run_query(sql1)
print(f"자재 건수: {len(res1)}")
print(json.dumps(res1[:5], ensure_ascii=False, indent=2))

# 2. NP.BLOCKNO Hex 직접검색 (86137217)
sql2 = "SELECT VF$OUID, MD$NUMBER, MD$DESC, SPEC, BLOCKNO FROM HDEL_DEFAULT.NORMALPART$VF WHERE UPPER(BLOCKNO) LIKE '%86137217%'"
print("--- 2. BLOCKNO LIKE '%86137217%' ---")
res2 = run_query(sql2)
print(f"자재 건수: {len(res2)}")
print(json.dumps(res2[:5], ensure_ascii=False, indent=2))

# 3. 만약 자재가 있다면, 해당 자재들이 PARTOFEBOM에 몇건이나 포함되는지
if res1 or res2:
    parts = res1 if res1 else res2
    ouid_list = ",".join([str(p['VF$OUID']) for p in parts[:50]])
    sql3 = f"SELECT COUNT(DISTINCT PRODUCTOUID) AS PROD_CNT, COUNT(*) AS BOM_CNT FROM HDEL_DEFAULT.PARTOFEBOM WHERE PARTOUID IN ({ouid_list})"
    print("--- 3. PARTOFEBOM 등장 건수 ---")
    res3 = run_query(sql3)
    print(json.dumps(res3, ensure_ascii=False, indent=2))
