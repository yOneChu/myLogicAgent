import os
import json
import urllib.parse
import urllib.request
import ssl
import pandas as pd

# ==============================================================================
# [설명] V호기 BOM 조회를 수행하고 결과를 CSV 및 Excel 파일로 저장하는 스크립트
# ==============================================================================

API_URL = "https://vault-in.hdel.co.kr:8070/api/executeQuery"
API_KEY = "subae"

def get_clean_sql():
    """
    [주요 함수] API 전달용 주석 제거 SQL 문장 반환
    """
    return """
WITH ouid AS (
    SELECT A.vf$ouid AS VFOID
      FROM HDEL_DEFAULT.product$vf A, HDEL_DEFAULT.product$id B
     WHERE A.vf$identity = B.id$ouid
       AND A.vf$ouid     = B.id$wip
       AND A.MD$NUMBER LIKE 'V%'
       AND A.MD$NUMBER NOT LIKE 'TEST%'
       AND A.MD$NUMBER NOT LIKE 'Q%'
)
SELECT (SELECT MD$NUMBER FROM HDEL_DEFAULT.PRODUCT$VF WHERE VF$OUID = PE.PRODUCTOUID) AS PARENTNO,
       (SELECT F.VF$VERSION FROM HDEL_DEFAULT.PRODUCT$VF F WHERE F.VF$OUID = PE.PRODUCTOUID) AS PARENT_VER,
       (SELECT PRODUCT.MD$STATUS FROM HDEL_DEFAULT.PRODUCT$VF PRODUCT WHERE PRODUCT.VF$OUID = PE.PRODUCTOUID) AS PROD_STATUS,
       (SELECT CASE WHEN LENGTH(PRODUCT.MD$CDATE) >= 8 
                    THEN SUBSTR(PRODUCT.MD$CDATE, 1, 4) || '-' || SUBSTR(PRODUCT.MD$CDATE, 5, 2) || '-' || SUBSTR(PRODUCT.MD$CDATE, 7, 2)
                    ELSE PRODUCT.MD$CDATE END
          FROM HDEL_DEFAULT.PRODUCT$VF PRODUCT WHERE PRODUCT.VF$OUID = PE.PRODUCTOUID) AS PROD_CDATE,
       (SELECT CASE WHEN LENGTH(PRODUCT.MD$MDATE) >= 8 
                    THEN SUBSTR(PRODUCT.MD$MDATE, 1, 4) || '-' || SUBSTR(PRODUCT.MD$MDATE, 5, 2) || '-' || SUBSTR(PRODUCT.MD$MDATE, 7, 2)
                    ELSE PRODUCT.MD$MDATE END
          FROM HDEL_DEFAULT.PRODUCT$VF PRODUCT WHERE PRODUCT.VF$OUID = PE.PRODUCTOUID) AS PROD_MODDATE,
       (SELECT HDEL_DEFAULT.COD(E.EL_ATYP) FROM HDEL_DEFAULT.ELV_INFO$ID A, HDEL_DEFAULT.ELV_INFO$VF E
         WHERE A.ID$OUID = E.VF$IDENTITY AND E.vf$ouid = A.id$wip
           AND E.MD$NUMBER = (SELECT F.MD$NUMBER FROM HDEL_DEFAULT.PRODUCT$VF F WHERE F.VF$OUID = PE.PRODUCTOUID)
           AND ROWNUM = 1) AS GISONG,
       (SELECT HDEL_DEFAULT.COD(E.EL_ABRAND) FROM HDEL_DEFAULT.ELV_INFO$ID A, HDEL_DEFAULT.ELV_INFO$VF E
         WHERE A.ID$OUID = E.VF$IDENTITY AND E.vf$ouid = A.id$wip
           AND E.MD$NUMBER = (SELECT F.MD$NUMBER FROM HDEL_DEFAULT.PRODUCT$VF F WHERE F.VF$OUID = PE.PRODUCTOUID)
           AND ROWNUM = 1) AS BRAND,
       (SELECT HDEL_DEFAULT.COD(E.EL_ASPD) FROM HDEL_DEFAULT.ELV_INFO$ID A, HDEL_DEFAULT.ELV_INFO$VF E
         WHERE A.ID$OUID = E.VF$IDENTITY AND E.vf$ouid = A.id$wip
           AND E.MD$NUMBER = (SELECT F.MD$NUMBER FROM HDEL_DEFAULT.PRODUCT$VF F WHERE F.VF$OUID = PE.PRODUCTOUID)
           AND ROWNUM = 1) AS EL_ASPD,
       (SELECT HDEL_DEFAULT.COD(E.EL_ACAPA) FROM HDEL_DEFAULT.ELV_INFO$ID A, HDEL_DEFAULT.ELV_INFO$VF E
         WHERE A.ID$OUID = E.VF$IDENTITY AND E.vf$ouid = A.id$wip
           AND E.MD$NUMBER = (SELECT F.MD$NUMBER FROM HDEL_DEFAULT.PRODUCT$VF F WHERE F.VF$OUID = PE.PRODUCTOUID)
           AND ROWNUM = 1) AS EL_ACAPA,
       (SELECT HDEL_DEFAULT.COD(E.EL_ASPSCD) FROM HDEL_DEFAULT.ELV_INFO$ID A, HDEL_DEFAULT.ELV_INFO$VF E
         WHERE A.ID$OUID = E.VF$IDENTITY AND E.vf$ouid = A.id$wip
           AND E.MD$NUMBER = (SELECT F.MD$NUMBER FROM HDEL_DEFAULT.PRODUCT$VF F WHERE F.VF$OUID = PE.PRODUCTOUID)
           AND ROWNUM = 1) AS ASPSCD,
       NP.MD$NUMBER  AS PARTNO,
       NP.MD$DESC    AS PARTNAME,
       NP.VF$VERSION AS PART_VERSION,
       NVL(NP.SPEC, '') AS SPEC,
       NVL(NP.G_L_CODE, '') AS GLCODE,
       PE.QTY AS PART_QTY,
       PE.CMT AS CMT,
       VP.UCHECK AS UCHECK
  FROM HDEL_DEFAULT.PARTOFEBOM PE
 INNER JOIN HDEL_DEFAULT.NORMALPART$VF NP ON PE.PARTOUID = NP.VF$OUID
  LEFT OUTER JOIN HDEL_DEFAULT.VARIABLEPART_NEW VP
    ON VP.PRODUCTOUID = PE.PRODUCTOUID AND VP.ASSOOUID = PE.ASSOOUID
 WHERE PE.PRODUCTOUID IN (SELECT VFOID FROM ouid)
 ORDER BY PARENTNO, PARTNO
"""

def fetch_sql_data(sql: str) -> list:
    """
    [주요 함수] SQL 쿼리를 API로 전달하여 JSON 결과 데이터를 가져오는 함수
    """
    query_string = urllib.parse.urlencode({"key": API_KEY, "sql": sql})
    url = f"{API_URL}?{query_string}"
    req = urllib.request.Request(url, headers={"Accept": "application/json"})
    context = ssl._create_unverified_context()
    with urllib.request.urlopen(req, context=context) as resp:
        return json.loads(resp.read().decode('utf-8'))

def export_v_bom_results():
    """
    [주요 함수] V호기 BOM 쿼리를 실행하여 output_csv 및 output_excel 폴더에 결과를 저장하는 메인 로직 함수
    """
    sql = get_clean_sql()

    print("[정보] V호기 BOM 추출 SQL 실행 중...")
    data = fetch_sql_data(sql)
    print(f"[성공] 총 {len(data):,}건의 BOM 데이터를 수집했습니다.")

    if not data:
        print("[경고] 데이터가 없습니다.")
        return

    df = pd.DataFrame(data)

    # 출력 폴더 설정 (RULE[file-folders.md] 기준)
    workspace_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
    csv_dir = os.path.join(workspace_root, "output_csv")
    excel_dir = os.path.join(workspace_root, "output_excel")

    os.makedirs(csv_dir, exist_ok=True)
    os.makedirs(excel_dir, exist_ok=True)

    csv_path = os.path.join(csv_dir, "v_products_bom_list.csv")
    excel_path = os.path.join(excel_dir, "v_products_bom_list.xlsx")

    # CSV 저장 (UTF-8 with BOM)
    df.to_csv(csv_path, index=False, encoding="utf-8-sig")
    print(f"[저장 완료] CSV 파일: {csv_path}")

    # Excel 저장
    with pd.ExcelWriter(excel_path, engine="openpyxl") as writer:
        df.to_excel(writer, index=False, sheet_name="V_BOM_List")
    print(f"[저장 완료] Excel 파일: {excel_path}")

if __name__ == "__main__":
    export_v_bom_results()
