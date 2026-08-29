import json
import urllib.parse
import urllib.request
import re
import os
import pandas as pd
from pathlib import Path

# 설정
WORKSPACE_ROOT = Path(r"c:\anti_workspace\myLogicAgent")
OUTPUT_CSV_DIR = WORKSPACE_ROOT / "output_csv"
OUTPUT_EXCEL_DIR = WORKSPACE_ROOT / "output_excel"
OUTPUT_CSV_DIR.mkdir(parents=True, exist_ok=True)
OUTPUT_EXCEL_DIR.mkdir(parents=True, exist_ok=True)

EXECUTE_QUERY_API = "https://vault-in.hdel.co.kr:8070/api/executeQuery"
PART_INFO_API = "https://vault-in.hdel.co.kr:8070/api/findPartInfoWithList"
API_KEY = "subae"
TARGET_PID = "EL_PA115A02"

# 1. 쿼리 정의 (테스트버전) - SPEC 30, KEY 20까지 추출
SQL_QUERY = f"""
SELECT H.PID, H.VERSION, H.HOUID,
       D.NO,
       NVL(D.ADDR, '-') AS ADDR,
       NVL(D.GOTO, '-') AS GOTO,
       NVL(D.REMARKS, '-') AS REMARKS,
       NVL(D.SPEC1, '-') AS SPEC1, NVL(D.CON1, '-') AS CON1,
       NVL(D.SPEC2, '-') AS SPEC2, NVL(D.CON2, '-') AS CON2,
       NVL(D.SPEC3, '-') AS SPEC3, NVL(D.CON3, '-') AS CON3,
       NVL(D.SPEC4, '-') AS SPEC4, NVL(D.CON4, '-') AS CON4,
       NVL(D.SPEC5, '-') AS SPEC5, NVL(D.CON5, '-') AS CON5,
       NVL(D.SPEC6, '-') AS SPEC6, NVL(D.CON6, '-') AS CON6,
       NVL(D.SPEC7, '-') AS SPEC7, NVL(D.CON7, '-') AS CON7,
       NVL(D.SPEC8, '-') AS SPEC8, NVL(D.CON8, '-') AS CON8,
       NVL(D.SPEC9, '-') AS SPEC9, NVL(D.CON9, '-') AS CON9,
       NVL(D.SPEC10, '-') AS SPEC10, NVL(D.CON10, '-') AS CON10,
       NVL(D.SPEC11, '-') AS SPEC11, NVL(D.CON11, '-') AS CON11,
       NVL(D.SPEC12, '-') AS SPEC12, NVL(D.CON12, '-') AS CON12,
       NVL(D.SPEC13, '-') AS SPEC13, NVL(D.CON13, '-') AS CON13,
       NVL(D.SPEC14, '-') AS SPEC14, NVL(D.CON14, '-') AS CON14,
       NVL(D.SPEC15, '-') AS SPEC15, NVL(D.CON15, '-') AS CON15,
       NVL(D.SPEC16, '-') AS SPEC16, NVL(D.CON16, '-') AS CON16,
       NVL(D.SPEC17, '-') AS SPEC17, NVL(D.CON17, '-') AS CON17,
       NVL(D.SPEC18, '-') AS SPEC18, NVL(D.CON18, '-') AS CON18,
       NVL(D.SPEC19, '-') AS SPEC19, NVL(D.CON19, '-') AS CON19,
       NVL(D.SPEC20, '-') AS SPEC20, NVL(D.CON20, '-') AS CON20,
       NVL(D.SPEC21, '-') AS SPEC21, NVL(D.CON21, '-') AS CON21,
       NVL(D.SPEC22, '-') AS SPEC22, NVL(D.CON22, '-') AS CON22,
       NVL(D.SPEC23, '-') AS SPEC23, NVL(D.CON23, '-') AS CON23,
       NVL(D.SPEC24, '-') AS SPEC24, NVL(D.CON24, '-') AS CON24,
       NVL(D.SPEC25, '-') AS SPEC25, NVL(D.CON25, '-') AS CON25,
       NVL(D.SPEC26, '-') AS SPEC26, NVL(D.CON26, '-') AS CON26,
       NVL(D.SPEC27, '-') AS SPEC27, NVL(D.CON27, '-') AS CON27,
       NVL(D.SPEC28, '-') AS SPEC28, NVL(D.CON28, '-') AS CON28,
       NVL(D.SPEC29, '-') AS SPEC29, NVL(D.CON29, '-') AS CON29,
       NVL(D.SPEC30, '-') AS SPEC30, NVL(D.CON30, '-') AS CON30,
       NVL(D.KEY1, '-') AS KEY1, NVL(D.VAL1, '-') AS VAL1,
       NVL(D.KEY2, '-') AS KEY2, NVL(D.VAL2, '-') AS VAL2,
       NVL(D.KEY3, '-') AS KEY3, NVL(D.VAL3, '-') AS VAL3,
       NVL(D.KEY4, '-') AS KEY4, NVL(D.VAL4, '-') AS VAL4,
       NVL(D.KEY5, '-') AS KEY5, NVL(D.VAL5, '-') AS VAL5,
       NVL(D.KEY6, '-') AS KEY6, NVL(D.VAL6, '-') AS VAL6,
       NVL(D.KEY7, '-') AS KEY7, NVL(D.VAL7, '-') AS VAL7,
       NVL(D.KEY8, '-') AS KEY8, NVL(D.VAL8, '-') AS VAL8,
       NVL(D.KEY9, '-') AS KEY9, NVL(D.VAL9, '-') AS VAL9,
       NVL(D.KEY10, '-') AS KEY10, NVL(D.VAL10, '-') AS VAL10,
       NVL(D.KEY11, '-') AS KEY11, NVL(D.VAL11, '-') AS VAL11,
       NVL(D.KEY12, '-') AS KEY12, NVL(D.VAL12, '-') AS VAL12,
       NVL(D.KEY13, '-') AS KEY13, NVL(D.VAL13, '-') AS VAL13,
       NVL(D.KEY14, '-') AS KEY14, NVL(D.VAL14, '-') AS VAL14,
       NVL(D.KEY15, '-') AS KEY15, NVL(D.VAL15, '-') AS VAL15,
       NVL(D.KEY16, '-') AS KEY16, NVL(D.VAL16, '-') AS VAL16,
       NVL(D.KEY17, '-') AS KEY17, NVL(D.VAL17, '-') AS VAL17,
       NVL(D.KEY18, '-') AS KEY18, NVL(D.VAL18, '-') AS VAL18,
       NVL(D.KEY19, '-') AS KEY19, NVL(D.VAL19, '-') AS VAL19,
       NVL(D.KEY20, '-') AS KEY20, NVL(D.VAL20, '-') AS VAL20
  FROM HDEL_DEFAULT.VARIANT_D D, HDEL_DEFAULT.VARIANT_H H
 WHERE H.PID = '{TARGET_PID}'
   AND H.VERSION = '-1'
   AND H.HOUID = D.HOUID
 ORDER BY TO_NUMBER(D.NO)
"""

def execute_query(sql):
    import ssl
    context = ssl._create_unverified_context()
    query_string = urllib.parse.urlencode({"key": API_KEY, "sql": sql.strip()})
    url = f"{EXECUTE_QUERY_API}?{query_string}"
    req = urllib.request.Request(url, method="GET", headers={"Accept": "application/json"})
    with urllib.request.urlopen(req, context=context) as response:
        body = response.read().decode('utf-8', errors='replace')
        return json.loads(body)

def find_part_info(part_list):
    import ssl
    context = ssl._create_unverified_context()
    if not part_list: return []
    data = urllib.parse.urlencode({
        "key": API_KEY,
        "PartNoList": ",".join(part_list)
    }).encode('utf-8')
    req = urllib.request.Request(PART_INFO_API, data=data, method="POST")
    with urllib.request.urlopen(req, context=context) as response:
        body = response.read().decode('utf-8', errors='replace')
        return json.loads(body)

def main():
    print(f"[{TARGET_PID}] 로직 데이터 추출 중...")
    data = execute_query(SQL_QUERY)
    
    if isinstance(data, dict):
        if "data" in data:
            data = data["data"]
        elif "resultList" in data:
            data = data["resultList"]
            
    if not isinstance(data, list) or len(data) == 0:
        print("로직 데이터가 없거나 응답 형식이 다릅니다.")
        return
    
    print(f"총 {len(data)}건의 로직 데이터 확인됨. 검증 시작...")
    
    # ADDR == 'MAIN' 이전 라인 검증 제외
    start_idx = -1
    for idx, row in enumerate(data):
        if str(row.get("ADDR")).strip() == "MAIN":
            start_idx = idx
            break
            
    if start_idx == -1:
        print("ADDR이 'MAIN'인 행이 없습니다. 검증을 종료합니다.")
        return
        
    data = data[start_idx:]
    print(f"'MAIN' 이후 {len(data)}건의 데이터에 대해 검증을 수행합니다.")
    
    errors = []
    seen_rows = set()
    addr_list = set([row.get("ADDR") for row in data if row.get("ADDR") != '-'])
    
    part_no_candidates = set()
    part_mapping = []

    for row in data:
        pid = row.get("PID", TARGET_PID)
        version = row.get("VERSION", "-1")
        no = row.get("NO", "")
        addr = row.get("ADDR", "-")
        
        # 1. SPEC/CON 짝 검증 (1~30)
        for i in range(1, 31):
            spec = str(row.get(f"SPEC{i}", "-")).strip()
            con = str(row.get(f"CON{i}", "-")).strip()
            
            if spec == "-" and con != "-":
                errors.append({
                    "PID": pid, "VERSION": version, "NO": no, "ADDR": addr,
                    "오류/경고": "ERROR", "검증 항목": "SPEC/CON 불일치",
                    "결함 상세 내용": f"SPEC{i}이 공백이나 CON{i}에 '{con}' 입력됨", "비고": "수정 필요"
                })
            elif spec != "-" and con == "-":
                errors.append({
                    "PID": pid, "VERSION": version, "NO": no, "ADDR": addr,
                    "오류/경고": "WARNING", "검증 항목": "SPEC만 존재",
                    "결함 상세 내용": f"SPEC{i}('{spec}')에 CON{i} 값이 비어있음", "비고": "[확인 필요]"
                })
                
        # 2. KEY/VAL 짝 검증 및 자재 추출 (1~20)
        for i in range(1, 21):
            key = str(row.get(f"KEY{i}", "-")).strip()
            val = str(row.get(f"VAL{i}", "-")).strip()
            
            if key == "-" and val != "-":
                errors.append({
                    "PID": pid, "VERSION": version, "NO": no, "ADDR": addr,
                    "오류/경고": "ERROR", "검증 항목": "KEY/VAL 불일치",
                    "결함 상세 내용": f"KEY{i}이 공백이나 VAL{i}에 '{val}' 입력됨", "비고": "수정 필요"
                })
            elif key != "-" and val == "-":
                errors.append({
                    "PID": pid, "VERSION": version, "NO": no, "ADDR": addr,
                    "오류/경고": "WARNING", "검증 항목": "KEY만 존재",
                    "결함 상세 내용": f"KEY{i}('{key}')에 VAL{i} 값이 비어있음", "비고": "[확인 필요]"
                })
                
            # KEY가 자재 속성이고 VAL이 있는 경우 추출
            if val != "-" and key not in ["L_CMT", "CALL", "CMT", "REMARKS"]:
                part_no_candidates.add(val)
                part_mapping.append((val, pid, version, no, addr))
                
        # 3. 분기 흐름 검증
        goto = str(row.get("GOTO", "-")).strip()
        if goto != "-" and goto != "STOP" and goto not in addr_list:
            errors.append({
                "PID": pid, "VERSION": version, "NO": no, "ADDR": addr,
                "오류/경고": "ERROR", "검증 항목": "분기 라벨 오류",
                "결함 상세 내용": f"GOTO에 지정된 '{goto}' 라벨이 존재하지 않음", "비고": "수정 필요"
            })
            
        # 4. 중복 행 검출
        row_signature_list = []
        for i in range(1, 31):
            row_signature_list.extend([str(row.get(f"SPEC{i}", "-")), str(row.get(f"CON{i}", "-"))])
        for i in range(1, 21):
            row_signature_list.extend([str(row.get(f"KEY{i}", "-")), str(row.get(f"VAL{i}", "-"))])
        row_signature_list.append(goto)
        
        signature = "|".join(row_signature_list)
        
        if all(x == '-' for x in row_signature_list):
            continue
            
        if signature in seen_rows:
            errors.append({
                "PID": pid, "VERSION": version, "NO": no, "ADDR": addr,
                "오류/경고": "ERROR", "검증 항목": "행 중복",
                "결함 상세 내용": f"해당 조건/산출/분기 조합이 이미 다른 NO에 존재함", "비고": "확인 필요"
            })
        else:
            seen_rows.add(signature)

    # 3단계: 자재번호 DB 배치 검증
    part_list = list(part_no_candidates)
    print(f"추출된 자재번호 수: {len(part_list)}개")
    
    valid_parts = set()
    for i in range(0, len(part_list), 200):
        chunk = part_list[i:i+200]
        try:
            res = find_part_info(chunk)
            if isinstance(res, list):
                for p_info in res:
                    # 응답 결과에서 자재번호 필드는 'partNo' 입니다.
                    valid_parts.add(p_info.get("partNo", ""))
        except Exception as e:
            print(f"자재 조회 API 에러 발생: {e}")
            
    for (val, pid, version, no, addr) in part_mapping:
        if val not in valid_parts:
            errors.append({
                "PID": pid, "VERSION": version, "NO": no, "ADDR": addr,
                "오류/경고": "ERROR", "검증 항목": "자재 DB 미존재",
                "결함 상세 내용": f"VAL 자재번호 '{val}'가 DB 부품 마스터에 없음", "비고": "자재 확인"
            })

    # 결과 저장
    df = pd.DataFrame(errors)
    if not df.empty:
        df['NO_INT'] = pd.to_numeric(df['NO'], errors='coerce')
        df = df.sort_values(by=['NO_INT']).drop(columns=['NO_INT'])
        
        csv_path = OUTPUT_CSV_DIR / f"{TARGET_PID}_test_validation.csv"
        excel_path = OUTPUT_EXCEL_DIR / f"{TARGET_PID}_test_validation.xlsx"
        
        df.to_csv(csv_path, index=False, encoding='utf-8-sig')
        df.to_excel(excel_path, index=False)
        
        print(f"검증 완료! 총 {len(errors)}건의 결함/경고가 발견되었습니다.")
        print(f" - CSV 저장 완료: {csv_path}")
        print(f" - Excel 저장 완료: {excel_path}")
    else:
        print("검증 완료! 결함이나 경고가 발견되지 않았습니다. (정합성 100%)")
        df = pd.DataFrame(columns=["PID", "VERSION", "NO", "ADDR", "오류/경고", "검증 항목", "결함 상세 내용", "비고"])
        csv_path = OUTPUT_CSV_DIR / f"{TARGET_PID}_test_validation.csv"
        excel_path = OUTPUT_EXCEL_DIR / f"{TARGET_PID}_test_validation.xlsx"
        df.to_csv(csv_path, index=False, encoding='utf-8-sig')
        df.to_excel(excel_path, index=False)

if __name__ == "__main__":
    main()
