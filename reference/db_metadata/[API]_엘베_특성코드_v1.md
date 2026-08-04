# 엘리베이터 API 정의서

> Antigravity 학습자료용 API 명세. 제공된 정보 기준으로만 작성되었으며, 미확인 항목은 `미확인`으로 표기함.

## 공통 정보

| 항목 | 값 |
|---|---|
| Base URL | `https://vault-in.hdel.co.kr:8070` |
| 공통 파라미터 | `key` |
| 인증 | 미확인 (`key` 파라미터로 구분되는 것으로 보임) |
| HTTP Method | GET |

### 공통 파라미터

| 파라미터 | 값 | 설명 |
|---|---|---|
| `key` | `subae` |  구분 키 |

---

## API 목록

| No | API 명 | Endpoint | 용도 |
|---|---|---|---|
| 01 | 특성코드 리스트 - 엘리베이터(육상) | `/api/getCodeList` | 사양별 특성(코드/값) 목록 조회 |
| 02 | 공사정보 필드 리스트 - 엘리베이터(육상) | `/api/getCodeField` | 공사정보 필드(사양) 목록 조회 |

---

## 01. 특성코드 리스트 - 엘리베이터(육상)

엘리베이터(육상) 사양에 정의된 특성코드 및 특성값 목록을 조회한다.

### Endpoint

```
https://vault-in.hdel.co.kr:8070/api/getCodeList
```

### Request Parameters

| 파라미터 | 타입 | 필수 | 값 | 설명 |
|---|---|---|---|---|
| `key` | string | Y | `subae` | 구분 키 |

### Response Columns

| 컬럼명 | 설명 |
|---|---|
| `code` | 사양 |
| `codeName` | 사양명 |
| `typeName` | 특성명 |
| `typeVal` | 특성값 |
| `name` | name |

### 호출 예시

```
GET https://vault-in.hdel.co.kr:8070/api/getCodeList?key=subae
```

---

## 02. 공사정보 필드 리스트 - 엘리베이터(육상)

엘리베이터(육상) 공사정보에 사용되는 필드(사양) 목록을 조회한다.

### Endpoint

```
https://vault-in.hdel.co.kr:8070/api/getCodeField
```

### Request Parameters

| 파라미터 | 타입 | 필수 | 값 | 설명 |
|---|---|---|---|---|
| `key` | string | Y | `subae` | 구분 키 |

### Response Columns

| 컬럼명 | 설명 |
|---|---|
| `NAME` | 사양 |
| `TIT` | 사양명 |

### 호출 예시

```
GET https://vault-in.hdel.co.kr:8070/api/getCodeField?key=subae
```

---

## 참고 사항

- API 01의 `code`(사양)와 API 02의 `NAME`(사양)은 동일한 "사양" 개념을 가리키며, 두 API를 연계할 때 매핑 키로 사용될 가능성이 있음. (미검증)
- 컬럼 네이밍 규칙이 API별로 다름: 01은 camelCase, 02는 대문자.
- 각 컬럼의 데이터 타입, null 허용 여부, 응답 래핑 구조(예: `{ data: [...] }` 여부)는 실제 응답 확인 필요.
