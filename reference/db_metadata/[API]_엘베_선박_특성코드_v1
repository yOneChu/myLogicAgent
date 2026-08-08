# 엘리베이터 & 선박 특성코드 및 공사정보 API 정의서

> 본 문서는 엘리베이터(육상) 및 선박 시스템의 특성코드와 공사정보 필드 조회를 위한 API 통합 명세서입니다.

---

## 1. 공통 정보

| 항목 | 값 | 설명 |
|---|---|---|
| **Base URL** | `https://vault-in.hdel.co.kr:8070` | API 서버 기본 URL |
| **HTTP Method** | `GET` | 전 API 공통 |
| **공통 파라미터** | `key=subae` | 시스템 구분 및 접근 인증 키 |
| **응답 포맷** | `JSON` | (상세 응답 구조는 실제 확인 필요) |

---

## 2. API 요약 및 비교 목록

| No | 도메인 | API 명 | Endpoint | 용도 |
|---|---|---|---|---|
| **01** | 엘리베이터(육상) | 특성코드 리스트 | `/api/getCodeList` | 사양별 특성(코드/값) 목록 조회 |
| **02** | 엘리베이터(육상) | 공사정보 필드 리스트 | `/api/getCodeField` | 공사정보 필드(사양) 목록 조회 |
| **03** | 선박 | 특성코드 리스트 | `/api/ship/getShipCode` | 사양별 특성(코드/값) 목록 조회 |
| **04** | 선박 | 공사정보 필드 리스트 | `/api/ship/getShipField` | 공사정보 필드(사양) 목록 조회 |

---

## 3. 상세 API 명세

### 3.1. 특성코드 리스트 API

사양별로 정의된 특성코드 및 특성값 목록을 조회합니다.

#### 1) 엔드포인트 비교
- **엘리베이터(육상)**: `https://vault-in.hdel.co.kr:8070/api/getCodeList`
- **선박**: `https://vault-in.hdel.co.kr:8070/api/ship/getShipCode`

#### 2) Request Parameters (공통)
| 파라미터 | 타입 | 필수 | 값 | 설명 |
|---|---|---|---|---|
| `key` | string | Y | `subae` | 구분 키 |

#### 3) Response Columns (공통)
| 컬럼명 | 설명 | 비고 |
|---|---|---|
| `code` | 사양 | 예: 사양 코드 |
| `codeName` | 사양명 | 사양에 대한 명칭 |
| `typeName` | 특성명 | 특성 이름 |
| `typeVal` | 특성값 | 특성에 대한 설정값 |
| `name` | name | 항목 명칭 |

#### 4) 호출 예시
- **엘리베이터(육상)**:
  ```http
  GET https://vault-in.hdel.co.kr:8070/api/getCodeList?key=subae
  ```
- **선박**:
  ```http
  GET https://vault-in.hdel.co.kr:8070/api/ship/getShipCode?key=subae
  ```

---

### 3.2. 공사정보 필드 리스트 API

공사정보에 사용되는 필드(사양) 목록을 조회합니다.

#### 1) 엔드포인트 비교
- **엘리베이터(육상)**: `https://vault-in.hdel.co.kr:8070/api/getCodeField`
- **선박**: `https://vault-in.hdel.co.kr:8070/api/ship/getShipField`

#### 2) Request Parameters (공통)
| 파라미터 | 타입 | 필수 | 값 | 설명 |
|---|---|---|---|---|
| `key` | string | Y | `subae` | 구분 키 |

#### 3) Response Columns (공통)
| 컬럼명 | 설명 | 비고 |
|---|---|---|
| `NAME` | 사양 | 사양 코드/명칭 |
| `TIT` | 사양명 | 사양 타이틀/설명 |

#### 4) 호출 예시
- **엘리베이터(육상)**:
  ```http
  GET https://vault-in.hdel.co.kr:8070/api/getCodeField?key=subae
  ```
- **선박**:
  ```http
  GET https://vault-in.hdel.co.kr:8070/api/ship/getShipField?key=subae
  ```

---

## 4. 특성 및 공사정보 컬럼 매핑 요약

| 구분 | 특성코드 API (Get Code List) | 공사정보 필드 API (Get Field List) |
|---|---|---|
| **도메인별 Endpoint** | - 엘베: `/api/getCodeList`<br>- 선박: `/api/ship/getShipCode` | - 엘베: `/api/getCodeField`<br>- 선박: `/api/ship/getShipField` |
| **사양 컬럼** | `code` (사양) | `NAME` (사양) |
| **사양명 컬럼** | `codeName` (사양명) | `TIT` (사양명) |
| **추가 컬럼** | `typeName` (특성명), `typeVal` (특성값), `name` (name) | - |
| **컬럼 표기법** | camelCase (`code`, `codeName`, `typeName`, `typeVal`) | UPPERCASE (`NAME`, `TIT`) |

---

## 5. 주요 참고 및 유의 사항

1. **사양 매핑 연계 가능성**:
   - 특성코드 API의 `code`(사양)와 공사정보 필드 API의 `NAME`(사양)은 동일한 사양 개념을 가리킵니다. 두 API 조회를 연계할 때 매핑 키로 활용할 수 있습니다.
2. **컬럼 대소문자 표기 규칙 차이**:
   - 특성코드 조회 API는 **camelCase** (`code`, `codeName`, `typeName`, `typeVal`) 구조입니다.
   - 공사정보 필드 조회 API는 **UPPERCASE** (`NAME`, `TIT`) 구조입니다.
3. **도메인 구분 라우팅**:
   - 엘리베이터(육상) API는 루트 경로(`/api/getCodeList`, `/api/getCodeField`)를 사용합니다.
   - 선박 API는 `/api/ship/` 하위 경로(`/api/ship/getShipCode`, `/api/ship/getShipField`)를 사용합니다.
4. **미확인 사항**:
   - 각 컬럼의 상세 데이터 타입 및 null 허용 여부, 응답 래핑 데이터 형태(예: `{ "data": [...] }`)는 실제 API 실행 후 결과 확인이 필요합니다.
