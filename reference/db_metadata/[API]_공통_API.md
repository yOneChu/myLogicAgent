# PLM 공통 API 테이블 명세서

이 문서는 PLM의 공통 API 정보를 정의합니다.


## 목차

01. 특성코드 리스트 - 엘리베이터(육상)
02. 공사정보 필드 리스트 - 엘리베이터(육상)
03. 특성코드 리스트 - 선박
04. 공사정보 필드 리스트 - 선박
05. 사용자 정보 조회 API


---

## 01. 특성코드 리스트 - 엘리베이터(육상)

엘리베이터(육상) 사양에 정의된 특성코드 및 특성값 목록을 조회한다.

### Endpoint
- GET 방식
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
- GET 방식
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

## 03. 특성코드 리스트 - 선박

선박 사양에 정의된 특성코드 및 특성값 목록을 조회한다.

### Endpoint
- GET 방식
```
https://vault-in.hdel.co.kr:8070/api/ship/getShipCode
```

### Request Parameters

| 파라미터 | 타입 | 필수 | 값 | 설명 |
|---|---|---|---|---|
| `key` | string | Y | `subae` | 선박 구분 키 |

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
GET https://vault-in.hdel.co.kr:8070/api/ship/getShipCode?key=subae
```

---

## 04. 공사정보 필드 리스트 - 선박

선박 공사정보에 사용되는 필드(사양) 목록을 조회한다.

### Endpoint
- GET 방식
```
https://vault-in.hdel.co.kr:8070/api/ship/getShipField
```

### Request Parameters

| 파라미터 | 타입 | 필수 | 값 | 설명 |
|---|---|---|---|---|
| `key` | string | Y | `subae` | 선박 구분 키 |

### Response Columns

| 컬럼명 | 설명 |
|---|---|
| `NAME` | 사양 |
| `TIT` | 사양명 |

### 호출 예시

```
GET https://vault-in.hdel.co.kr:8070/api/ship/getShipField?key=subae
```

---


## 05. 사용자 정보 조회 API


- **URL**: `https://vault-in.hdel.co.kr:8070/api/getUserInfoList`
- **HTTP Method**: `GET`
- **파라미터**:
  | 파라미터명 | 타입 | 필수 여부 | 설정값 | 설명 |
  |---|---|---|---|---|
  | `key` | String | 필수 | `subae` | API 접근 인증 키 |

- **호출 예시**:
  ```text
  GET https://vault-in.hdel.co.kr:8070/api/getUserInfoList?key=subae
  ```
  
- **반환형식**
```json
{
"OID": "",  //사용자 key ouid
"sabun": "", //사번
"name": "", //사용자 이름
"email": "" //이메일
}
```