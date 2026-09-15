# -*- coding: utf-8 -*-
"""
2026년 B120B03 벨런스웨이트 사용 현장 종합 분석 스크립트 (수정본)
"""

import json
import os
import ssl
from urllib.parse import urlencode
from urllib.request import Request, urlopen

API_URL = "https://vault-in.hdel.co.kr:8070/api/executeQuery"
API_KEY = "subae"

def run_query(sql: str):
    query_string = urlencode({"key": API_KEY, "sql": sql})
    url = f"{API_URL}?{query_string}"
    req = Request(url, headers={"Accept": "application/json", "User-Agent": "Mozilla/5.0"})
    context = ssl._create_unverified_context()
    with urlopen(req, timeout=120, context=context) as resp:
        return json.loads(resp.read().decode("utf-8", errors="replace"))

def main():
    print("=== B120B03 2026년 전체 사용 현장(호기) 목록 및 주요 사양 추출 ===")
    
    # B120B03 블록 SF$OUID = 2249421335 -> HEX: 86137217
    
    sql_detail = """
    WITH ouid AS (
        SELECT A.vf$ouid AS VFOID,
               A.MD$NUMBER AS HOGI,
               A.MD$STATUS AS PROD_STATUS,
               SUBSTR(A.MD$MDATE, 1, 8) AS MOD_DATE
          FROM HDEL_DEFAULT.product$vf A, HDEL_DEFAULT.product$id B
         WHERE A.vf$identity = B.id$ouid
           AND A.vf$ouid     = B.id$wip
           AND A.MD$NUMBER NOT LIKE 'TEST%'
           AND A.MD$NUMBER NOT LIKE 'Q%'
           AND SUBSTR(A.MD$MDATE, 1, 4) = '2026'
           AND A.MD$STATUS = 'RLS'
    ),
    b120b03_parts AS (
        SELECT NP.VF$OUID AS PARTOUID,
               NP.MD$NUMBER AS PARTNO,
               NP.MD$DESC AS PARTNAME,
               NP.SPEC AS SPEC,
               NP.G_L_CODE AS GLCODE
          FROM HDEL_DEFAULT.NORMALPART$VF NP
         WHERE LOWER(NP.BLOCKNO) LIKE '%86137217%'
    )
    SELECT O.HOGI,
           O.MOD_DATE,
           BP.PARTNO,
           BP.PARTNAME,
           BP.SPEC,
           PE.QTY AS PART_QTY,
           PE.CMT AS CMT,
           (SELECT HDEL_DEFAULT.COD(E.EL_ABRAND) FROM HDEL_DEFAULT.ELV_INFO$ID A, HDEL_DEFAULT.ELV_INFO$VF E
             WHERE A.ID$OUID = E.VF$IDENTITY AND E.vf$ouid = A.id$wip AND E.MD$NUMBER = O.HOGI) AS BRAND,
           (SELECT HDEL_DEFAULT.COD(E.EL_ATYP) FROM HDEL_DEFAULT.ELV_INFO$ID A, HDEL_DEFAULT.ELV_INFO$VF E
             WHERE A.ID$OUID = E.VF$IDENTITY AND E.vf$ouid = A.id$wip AND E.MD$NUMBER = O.HOGI) AS GISONG,
           (SELECT HDEL_DEFAULT.COD(E.EL_ASPD) FROM HDEL_DEFAULT.ELV_INFO$ID A, HDEL_DEFAULT.ELV_INFO$VF E
             WHERE A.ID$OUID = E.VF$IDENTITY AND E.vf$ouid = A.id$wip AND E.MD$NUMBER = O.HOGI) AS SPEED,
           (SELECT HDEL_DEFAULT.COD(E.EL_ACAPA) FROM HDEL_DEFAULT.ELV_INFO$ID A, HDEL_DEFAULT.ELV_INFO$VF E
             WHERE A.ID$OUID = E.VF$IDENTITY AND E.vf$ouid = A.id$wip AND E.MD$NUMBER = O.HOGI) AS CAPA,
           (SELECT HDEL_DEFAULT.COD(E.EL_ASPSCD) FROM HDEL_DEFAULT.ELV_INFO$ID A, HDEL_DEFAULT.ELV_INFO$VF E
             WHERE A.ID$OUID = E.VF$IDENTITY AND E.vf$ouid = A.id$wip AND E.MD$NUMBER = O.HOGI) AS PLANT,
           (SELECT HDEL_DEFAULT.COD(E.EL_ETHRU) FROM HDEL_DEFAULT.ELV_INFO$ID A, HDEL_DEFAULT.ELV_INFO$VF E
             WHERE A.ID$OUID = E.VF$IDENTITY AND E.vf$ouid = A.id$wip AND E.MD$NUMBER = O.HOGI) AS ETHRU,
           (SELECT HDEL_DEFAULT.COD(E.EL_ECWSF) FROM HDEL_DEFAULT.ELV_INFO$ID A, HDEL_DEFAULT.ELV_INFO$VF E
             WHERE A.ID$OUID = E.VF$IDENTITY AND E.vf$ouid = A.id$wip AND E.MD$NUMBER = O.HOGI) AS CWT_SAFETY,
           (SELECT E.EL_ECBA FROM HDEL_DEFAULT.ELV_INFO$ID A, HDEL_DEFAULT.ELV_INFO$VF E
             WHERE A.ID$OUID = E.VF$IDENTITY AND E.vf$ouid = A.id$wip AND E.MD$NUMBER = O.HOGI) AS CWT_BALANCE,
           (SELECT E.EL_ECBB FROM HDEL_DEFAULT.ELV_INFO$ID A, HDEL_DEFAULT.ELV_INFO$VF E
             WHERE A.ID$OUID = E.VF$IDENTITY AND E.vf$ouid = A.id$wip AND E.MD$NUMBER = O.HOGI) AS CAR_BB,
           (SELECT E.EL_ECAA FROM HDEL_DEFAULT.ELV_INFO$ID A, HDEL_DEFAULT.ELV_INFO$VF E
             WHERE A.ID$OUID = E.VF$IDENTITY AND E.vf$ouid = A.id$wip AND E.MD$NUMBER = O.HOGI) AS CAR_AA
      FROM HDEL_DEFAULT.PARTOFEBOM PE
     INNER JOIN ouid O ON PE.PRODUCTOUID = O.VFOID
     INNER JOIN b120b03_parts BP ON PE.PARTOUID = BP.PARTOUID
    """
    
    res = run_query(sql_detail)
    print(f"총 조회 건수(BOM 행 기준): {len(res)}건")
    
    if res:
        with open("scripts/db_query/b120b03_2026_raw.json", "w", encoding="utf-8") as f:
            json.dump(res, f, ensure_ascii=False, indent=2)
        print("raw JSON 데이터 저장 완료: scripts/db_query/b120b03_2026_raw.json")

if __name__ == "__main__":
    main()
