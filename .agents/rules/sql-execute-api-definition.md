---
trigger: always_on
---

# SQL 쿼리 수행 API 정의서

## 1. 문서 목적

이 문서는 LLM이 자연어를 바탕으로 생성한 SQL을 실행하기 위해 사용하는 API 정보를 정의한다.
LLM은 사용자의 요청을 해석하여 SQL을 생성할 수 있지만, 데이터의 안전 및 보안을 위해 반드시 `SELECT` 쿼리만 생성하고 실행해야 한다.
이 API는 SQL 조회 결과를 JSON 형식으로 반환한다.

---

## 2. API 개요

| 항목 | 내용 |
|---|---|
| API 명 | SQL 쿼리 수행 API |
| 목적 | 작성된 SQL 조회 쿼리를 실행하고 결과 데이터를 JSON 형식으로 반환 |
| 호출 방식 | HTTP 요청 |
| 결과 형식 | JSON |
| 허용 SQL | `SELECT` 문 |
| 금지 SQL | `INSERT`, `UPDATE`, `DELETE`, `MERGE`, `ALTER`, `DROP`, `TRUNCATE`, `CREATE` 등 데이터 변경 또는 구조 변경 SQL |

---

## 3. API URL

```text
https://vault-in.hdel.co.kr:8070/apiv2/executeQuery?key=subae&sql=
```

SQL 쿼리는 `sql` 파라미터 값으로 전달한다.

---

## 4. 요청 파라미터

| 파라미터 | 필수 여부 | 설명 |
|---|---:|---|
| `key` | 필수 | API 접근 키. 현재 값은 `subae`를 사용 |
| `sql` | 필수 | 실행할 SQL 조회 쿼리 |

---

## 5. 요청 예시

### 5.1 기본 요청 구조

```text
https://vault-in.hdel.co.kr:8070/apiv2/executeQuery?key=subae&sql={SQL_QUERY}
```

### 5.2 SQL 예시

```sql
SELECT
    A.MD$NUMBER AS REQNO,
    A.MD$STATUS,
    A.MD$DESC,
    A.MANAGER,
    A.HOGI
FROM NEWPLMDESIGNREQUEST$VF A
WHERE A.MD$NUMBER = '03412'
```

### 5.3 API 호출 예시

아래 예시는 이해를 돕기 위한 형태이다. 실제 호출 시에는 SQL 문자열을 URL 인코딩하여 전달해야 한다.

```text
https://vault-in.hdel.co.kr:8070/apiv2/executeQuery?key=subae&sql=SELECT%20A.MD%24NUMBER%20AS%20REQNO%2C%20A.MD%24STATUS%20FROM%20NEWPLMDESIGNREQUEST%24VF%20A
```

---

## 6. 응답 형식

API 응답은 JSON 형식으로 반환된다.

응답 구조는 실행 결과에 따라 달라질 수 있으나, 기본적으로 SQL 조회 결과의 컬럼명과 데이터가 포함된다.

예시:

```json
[
  {
    "REQNO": "03412",
    "MD$STATUS": "RLS",
    "MD$DESC": "설계 요청 제목",
    "MANAGER": "담당자명",
    "HOGI": "대표호기"
  }
]
```

---

## 7. LLM SQL 생성 규칙

LLM은 이 API를 사용할 SQL을 생성할 때 다음 규칙을 반드시 따른다.

1. 반드시 `SELECT` 문만 생성한다.
2. 데이터 수정, 삭제, 생성, 테이블 구조 변경 SQL은 절대 생성하지 않는다.
3. 사용자 요청이 수정, 삭제, 반영, 변경, 저장, 생성 등 데이터 변경을 의미하더라도 SQL을 작성하지 않는다.
4. 사용자가 데이터 변경성 요청을 한 경우, 조회용 SQL만 가능하다고 안내한다.
5. SQL 실행 전 생성한 SQL이 `SELECT`로 시작하는지 검증한다.
6. `SELECT` 앞에 주석, 공백, 세미콜론, 다른 명령문을 섞어 우회하지 않는다.
7. 여러 SQL 문장을 세미콜론으로 연결하지 않는다.
8. 조회 목적에 필요한 컬럼과 조건만 포함한다.
9. 과도하게 많은 데이터를 조회할 가능성이 있으면 기간 조건, 요청번호, 담당자, 상태 등의 필터를 우선 적용한다.
10. 사용자의 조건이 불명확하면 임의로 수정성 SQL을 만들지 말고 확인 질문을 한다.
11. PLM의 데이터가 방대하기 때문에 대용량을 대상으로 검증하는 등 쿼리는 작성하지 않도록하고, 요청자한테 안내한다.
12. 대용량 검증 요청의 경우 꼭 기간 범위를 입력하라고 요청자한테 문의한다.
13. 대량 조회가 우려되는 경우 기간 조건 또는 건수 제한 조건을 꼭 추가한다.


---

## 8. 금지 SQL 예시

아래와 같은 SQL은 절대 생성하거나 API로 전달하면 안 된다.

```sql
UPDATE NEWPLMDESIGNREQUEST$VF
SET MD$STATUS = 'RLS'
WHERE MD$NUMBER = '03412'
```

```sql
DELETE FROM NEWPLMDESIGNREQUEST$VF
WHERE MD$NUMBER = '03412'
```

```sql
ALTER TABLE NEWPLMDESIGNREQUEST$VF ADD TEST_COL VARCHAR2(100)
```

```sql
DROP TABLE NEWPLMDESIGNREQUEST$VF
```

```sql
TRUNCATE TABLE NEWPLMDESIGNREQUEST$VF
```

---

## 9. 허용 SQL 예시

아래와 같은 조회 SQL만 허용한다.

```sql
SELECT
    A.MD$NUMBER AS REQNO,
    A.MD$STATUS,
    A.MD$DESC,
    A.MANAGER,
    A.HOGI
FROM NEWPLMDESIGNREQUEST$VF A
WHERE A.MD$NUMBER = '03412'
```

```sql
SELECT
    SUBSTR(A.MD$CDATE, 1, 6) AS CRE_MONTH,
    COUNT(*) AS CNT
FROM NEWPLMDESIGNREQUEST$VF A
WHERE SUBSTR(A.MD$CDATE, 1, 4) = '2026'
GROUP BY SUBSTR(A.MD$CDATE, 1, 6)
ORDER BY CRE_MONTH
```

---

## 10. API 사용 절차

LLM 또는 시스템은 다음 절차로 API를 사용한다.

1. 사용자의 자연어 요청을 분석한다.
2. 조회 대상 테이블과 컬럼을 결정한다.
3. `SELECT` SQL을 생성한다.
4. SQL이 `SELECT` 문인지 검증한다.
5. 금지 키워드가 포함되어 있는지 검증한다.
6. SQL 문자열을 URL 인코딩한다.
7. `sql` 파라미터에 인코딩된 SQL을 전달한다.
8. API에서 반환된 JSON 결과를 사용자 요청에 맞게 요약, 분석 또는 표 형태로 제공한다.

---

## 11. 권장 검증 로직

API 호출 전 SQL 문자열에 대해 다음 검증을 수행하는 것을 권장한다.

### 11.1 허용 조건

- 앞뒤 공백 제거 후 SQL이 `SELECT`로 시작해야 한다.
- 단일 조회문이어야 한다.
- 조회 대상과 조건이 사용자 요청과 일치해야 한다.

### 11.2 차단 조건

다음 키워드가 포함된 SQL은 차단한다.

```text
INSERT
UPDATE
DELETE
MERGE
ALTER
DROP
TRUNCATE
CREATE
REPLACE
GRANT
REVOKE
COMMIT
ROLLBACK
EXEC
EXECUTE
CALL
```

세미콜론을 사용한 다중 쿼리 실행도 차단하는 것을 권장한다.

---

## 12. LLM 시스템 프롬프트 예시

아래 문장은 LLM의 시스템 프롬프트 또는 API 사용 지침에 포함할 수 있다.

```text
너는 사내 PLM 데이터를 조회하기 위한 SQL 생성 및 API 호출 도우미이다.

사용자의 자연어 요청을 분석하여 SELECT SQL만 생성한다.
생성된 SQL은 SQL 쿼리 수행 API의 sql 파라미터로 전달된다.

API URL은 다음 형식을 사용한다.
https://vault-in.hdel.co.kr:8070/apiv2/executeQuery?key=subae&sql={URL_ENCODED_SQL}

데이터 안전 및 보안을 위해 INSERT, UPDATE, DELETE, MERGE, ALTER, DROP, TRUNCATE, CREATE 등 데이터 변경 또는 구조 변경 SQL은 절대 생성하지 않는다.
사용자가 수정, 삭제, 반영, 저장 등 데이터 변경을 요청하면 SQL을 생성하지 말고, 조회만 가능하다고 안내한다.

SQL은 반드시 SELECT로 시작하는 단일 조회문이어야 한다.
SQL을 API로 전달하기 전 URL 인코딩한다.
API 응답은 JSON 형식이며, 반환된 JSON 데이터를 사용자의 요청에 맞게 요약하거나 표 형태로 정리한다.
```

---

## 13. 보안 주의사항

이 API는 SQL 문자열을 직접 전달받아 실행하는 구조이므로 SQL 생성 단계에서 보안 검증이 매우 중요하다.

다음 사항을 반드시 준수한다.

- 사용자 입력을 그대로 SQL에 삽입하지 않는다.
- 조회 조건 값은 문자열 리터럴로 안전하게 처리한다.
- 사용자가 SQL 일부를 직접 입력하더라도 금지 키워드를 검사한다.
- `SELECT` 이외의 SQL은 실행하지 않는다.
- 다중 문장 실행을 허용하지 않는다.
- 대량 조회가 우려되는 경우 기간 조건 또는 건수 제한 조건을 추가한다.