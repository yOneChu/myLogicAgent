---
trigger: always_on
---

# [업무 지시서] PLM 로직 및 부품번호 DB 정합성 검증

## 1. 업무 목적
- 지정된 로직 PID의 구문/문법 정합성을 검증합니다.
- `reference/db_metadata/pid_query.sql` 기준 DB 조회를 통해 PID 상세 로직을 추출하고, 문법 규칙 검증 및 `VAL1`~`VAL20` 에 정의된 값 자재번호의 실제 DB에 이는지 부품 API 배치 조회를 통해 교차 검증합니다.
- 로직의 검증은 추출된 데이터의 ADDR 열 값이 'MAIN' 인 라인 부터 검증을 수행한다. MAIN 이전 라인은 검증 제외

---

## 2. 검증 대상 및 참조 문서
- **검증 PID**: [검증할 PID 및 Version 입력 (예: PID='CERTI_E331A', VERSION='12')]
- 검증할 PID만 입력면 기본적으로 최신버전으로 조회 합니다.
- **참조 문서/코드**:
  1) PID 쿼리 생성을 위한 DB 정의서
    - 호출방식 : GET
    - API : https://vault-in.hdel.co.kr:8070/api/getLogicVerifyAsDB?key=subae&type=PID_DB_DOCUMENT
    - 반환타입 : String
  2) PID 추출 쿼리: `reference/db_metadata/pid_query.sql`
  3) 부품 속성 정보 API: `reference/db_metadata/[API]_BOM_PART.md`
  4) 로직 문법 규칙: `logic-syntax.md`
  5) BOM 정합성 규칙: `logic-BOM정합성_작성수정_rule.md`
  6) DB 조회, 쿼리 작성 규칙, 쿼리 수행 API 정의서
    - 호출방식 : GET
    - API : https://vault-in.hdel.co.kr:8070/api/getLogicVerifyAsDB?key=subae&type=QUERY_EXECUTE_API
    - 반환타입 : String

---

## 3. 단계별 수행 절차

### 1단계: PID 로직 데이터 추출 (SQL API 활용)
1. `reference/db_metadata/pid_query.sql`의 SQL 구조를 사용하여 대상 PID의 Header/Detail 데이터를 추출합니다.
   - **조회 대상 테이블**: `HDEL_DEFAULT.VARIANT_H` (H), `HDEL_DEFAULT.VARIANT_D` (D)
   - **조회 조건**: `H.PID = '{대상_PID}' AND H.VERSION = '{대상_VERSION}' AND H.HOUID = D.HOUID`
   - **정렬 기준**: `ORDER BY TO_NUMBER(D.NO)`
   - **추출 컬럼**: `PID`, `VERSION`, `HOUID`, `NO`, `ADDR`, `GOTO`, `REMARKS`, `SPEC1`~`30`, `CON1`~`30`, `KEY1`~`20`, `VAL1`~`20`
   -  **추가 쿼리 작성 규칙**: 최신 버전, 테스트 버전 조회 및 기타 응용 조회가 필요한 경우에는 반드시 `PID 쿼리 생성을 위한 DB 정의서`의 조인 규칙(`VARIANT_ID.LAST_HOUID` 매핑 등)을 참고하여 쿼리를 작성합니다.
2. SQL 쿼리 수행 API (`https://vault-in.hdel.co.kr:8070/api/executeQuery?key=subae&sql=...`)를 호출하여 JSON 데이터를 가져옵니다.

### 2단계: 로직 문법 및 구조 정합성 검증
수집된 로직 데이터(`D.NO` 순)를 행 단위 및 전체 구조 단위로 검증합니다.

1. **SPEC / CON 조건 쌍 검증**:
   - `SPEC{n}`과 `CON{n}`의 짝 불일치 확인
   - `SPEC`이 공백(`-`)이지만 `CON`에 값이 존재하는 문법 오류 산출
2. **KEY / VAL 산출 쌍 검증**:
   - `KEY{n}`과 `VAL{n}`의 짝 불일치 확인
3. **행 중복 검증**:
   - `ADDR`, `REMARKS`를 제외한 `SPEC1~30 + CON1~30 + KEY1~20 + VAL1~20 + GOTO` 조합이 동일한 중복 행 검출
4. **분기 라벨(GOTO / ADDR) 검증**:
   - `GOTO`에 지정된 라벨이 전체 행의 `ADDR` 목록 중에 실제하는지 검증 (`STOP` 제외)



### 3단계: VAL(부품/자재번호) DB 존재 여부 배치 교차 검증
1. **자재번호 추출 및 필터링**:
   - 추출된 전체 `VAL1`~`VAL20` 데이터 값만 추출합니다.
   - 추출된 자재번호 목록에서 중복을 제거합니다.
2. **배치(Batch) API 호출 (최대 200개 단위)**:
   - 중복 제거된 자재번호 목록을 **최대 200개씩** 청크(Chunk)로 나눕니다.
   - 각 청크를 쉼표(`,`) 구분기호로 연결하여 문자열을 생성합니다. (예: `부품번호1,부품번호2,...`)
   - `reference/db_metadata/[API]_BOM_PART.md` 명세에 따라 아래 API를 `POST` 호출합니다.
     - **Endpoint**: `https://vault-in.hdel.co.kr:8070/api/findPartInfoWithList`
     - **Body / Parameters**:
       - `key`: `subae`
       - `PartNoList`: `쉼표로_연결된_자재번호_최대200개`
3. **존재 여부 판정**:
   - API 응답 결과 데이터셋에 반환된 자재번호는 '정상(존재)'으로 판정합니다.
   - 요청 목록에는 포함되었으나 API 응답 결과에 자재 정보가 없는 자재번호는 **'DB 미존재 자재' ERROR**로 매핑합니다.

### 4단계: 결과 집계 및 파일 출력
- 검증된 요약 결과를 정리하고, 상세 검증 리포트를 파일로 생성합니다.
  - CSV 파일: `output_csv/` 폴더 저장 (`/script/db_query/query_to_csv.py` 활용)
  - Excel 파일: `output_excel/` 폴더 저장 (`/script/db_query/query_to_excel.py` 활용)

---

## 4. 검증 결과 리포트 출력 포맷

| PID | VERSION | NO | ADDR | 오류/경고 | 검증 항목 | 결함 상세 내용 | 비고 |
|---|---|---|---|---|---|---|---|
| CERTI_E331A | 12 | 1 | MAIN | ERROR | SPEC/CON 오류 | SPEC1이 공백이나 CON1에 'KR00' 입력됨 | 수정 필요 |
| CERTI_E331A | 12 | 5 | STEP_02 | ERROR | 자재 DB 미존재 | VAL1 자재번호 '12345678901' (11자리)가 부품 API 조회 결과에 없음 | 자재 확인 |
| CERTI_E331A | 12 | 8 | STEP_03 | WARNING | SPEC만 존재 | SPEC2('EL_ECBB')에 CON2 값이 비어있음 | [확인 필요] |

---

## 5. 제약 및 주의사항
- API 요청 시 1회당 **최대 200개 초과 금지** (200개 단위 분할 POST 요청).
- `query.sql`과 같이 `NVL(..., '-')` 처리된 공백 값(`-`)을 올바르게 공백 조건으로 해석하여 검증할 것.