import subprocess
import sys
from pathlib import Path

# SQL Query 1: Brand Summary
sql_brand = """
WITH ouid AS (
    SELECT A.vf$ouid AS VFOID,
           A.MD$NUMBER AS HOGI
      FROM HDEL_DEFAULT.product$vf A, HDEL_DEFAULT.product$id B
     WHERE A.vf$identity = B.id$ouid
       AND A.vf$ouid     = B.id$wip
       AND A.MD$NUMBER NOT LIKE 'TEST%'
       AND A.MD$NUMBER NOT LIKE 'Q%'
       AND SUBSTR(A.MD$MDATE, 1, 4) = '2026'
       AND A.MD$STATUS = 'RLS'
),
b181b_parts AS (
    SELECT NP.VF$OUID
      FROM HDEL_DEFAULT.NORMALPART$VF NP
     WHERE NP.BLOCKNO LIKE '%8613724a%'
),
hogi_b181b AS (
    SELECT DISTINCT PE.PRODUCTOUID AS VFOID, O.HOGI
      FROM HDEL_DEFAULT.PARTOFEBOM PE
     INNER JOIN b181b_parts BP ON PE.PARTOUID = BP.VF$OUID
     INNER JOIN ouid O ON PE.PRODUCTOUID = O.VFOID
),
hogi_elv AS (
    SELECT E.MD$NUMBER AS HOGI,
           HDEL_DEFAULT.COD(E.EL_ABRAND) AS BRAND
      FROM HDEL_DEFAULT.ELV_INFO$ID A, HDEL_DEFAULT.ELV_INFO$VF E
     WHERE A.ID$OUID = E.VF$IDENTITY AND E.vf$ouid = A.id$wip
)
SELECT NVL(E.BRAND, '미지정') AS BRAND,
       COUNT(DISTINCT H.VFOID) AS HOGI_CNT
  FROM hogi_b181b H
  LEFT OUTER JOIN hogi_elv E ON H.HOGI = E.HOGI
 GROUP BY NVL(E.BRAND, '미지정')
 ORDER BY HOGI_CNT DESC
"""

# SQL Query 2: Brand + Gisong Summary
sql_gisong = """
WITH ouid AS (
    SELECT A.vf$ouid AS VFOID,
           A.MD$NUMBER AS HOGI
      FROM HDEL_DEFAULT.product$vf A, HDEL_DEFAULT.product$id B
     WHERE A.vf$identity = B.id$ouid
       AND A.vf$ouid     = B.id$wip
       AND A.MD$NUMBER NOT LIKE 'TEST%'
       AND A.MD$NUMBER NOT LIKE 'Q%'
       AND SUBSTR(A.MD$MDATE, 1, 4) = '2026'
       AND A.MD$STATUS = 'RLS'
),
b181b_parts AS (
    SELECT NP.VF$OUID
      FROM HDEL_DEFAULT.NORMALPART$VF NP
     WHERE NP.BLOCKNO LIKE '%8613724a%'
),
hogi_b181b AS (
    SELECT DISTINCT PE.PRODUCTOUID AS VFOID, O.HOGI
      FROM HDEL_DEFAULT.PARTOFEBOM PE
     INNER JOIN b181b_parts BP ON PE.PARTOUID = BP.VF$OUID
     INNER JOIN ouid O ON PE.PRODUCTOUID = O.VFOID
),
hogi_elv AS (
    SELECT E.MD$NUMBER AS HOGI,
           HDEL_DEFAULT.COD(E.EL_ABRAND) AS BRAND,
           HDEL_DEFAULT.COD(E.EL_ATYP) AS GISONG
      FROM HDEL_DEFAULT.ELV_INFO$ID A, HDEL_DEFAULT.ELV_INFO$VF E
     WHERE A.ID$OUID = E.VF$IDENTITY AND E.vf$ouid = A.id$wip
)
SELECT NVL(E.BRAND, '미지정') AS BRAND,
       NVL(E.GISONG, '미지정') AS GISONG,
       COUNT(DISTINCT H.VFOID) AS HOGI_CNT
  FROM hogi_b181b H
  LEFT OUTER JOIN hogi_elv E ON H.HOGI = E.HOGI
 GROUP BY NVL(E.BRAND, '미지정'), NVL(E.GISONG, '미지정')
 ORDER BY BRAND, HOGI_CNT DESC
"""

# Save SQL files
Path("scripts/db_query/b181b_brand_summary_2026.sql").write_text(sql_brand, encoding="utf-8")
Path("scripts/db_query/b181b_brand_gisong_summary_2026.sql").write_text(sql_gisong, encoding="utf-8")

# Execute query_to_csv and query_to_excel
python_exe = sys.executable

subprocess.run([python_exe, "scripts/db_query/query_to_csv.py", "--sql-file", "scripts/db_query/b181b_brand_summary_2026.sql", "--output", "output_csv/b181b_brand_summary_2026.csv", "--insecure"], check=True)
subprocess.run([python_exe, "scripts/db_query/query_to_excel.py", "--sql-file", "scripts/db_query/b181b_brand_summary_2026.sql", "--output", "b181b_brand_summary_2026.xlsx", "--insecure"], check=True)

subprocess.run([python_exe, "scripts/db_query/query_to_csv.py", "--sql-file", "scripts/db_query/b181b_brand_gisong_summary_2026.sql", "--output", "output_csv/b181b_brand_gisong_summary_2026.csv", "--insecure"], check=True)
subprocess.run([python_exe, "scripts/db_query/query_to_excel.py", "--sql-file", "scripts/db_query/b181b_brand_gisong_summary_2026.sql", "--output", "b181b_brand_gisong_summary_2026.xlsx", "--insecure"], check=True)

print("All CSV and Excel files generated successfully.")
