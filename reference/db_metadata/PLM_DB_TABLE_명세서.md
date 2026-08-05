# PLM DB 테이블 명세서

이 문서는 PLM DB의 메타데이터 정의서 정보를 정의합니다.

---

## 01. 영업사양 메타 정보 조회 API
LLM 및 에이전트가 영업사양 정보 추출 및 SQL 쿼리를 생성하기 위해 참고하는 **메타데이터 정의서**를 조회합니다.

- **URL**: `https://vault-in.hdel.co.kr:8070/api/getSalesMetaInfo`
- **HTTP Method**: `GET`
- **파라미터**:
  | 파라미터명 | 타입 | 필수 여부 | 설정값 | 설명 |
  |---|---|---|---|---|
  | `key` | String | 필수 | `subae` | API 접근 인증 키 |

- **호출 예시**:
  ```text
  GET https://vault-in.hdel.co.kr:8070/api/getSalesMetaInfo?key=subae
  ```

---


## 비표준사양검토 메타 정보 조회 API
LLM 및 에이전트가 비표준사양검토 정보 추출 및 SQL 쿼리를 생성하기 위해 참고하는 **메타데이터 정의서**를 조회합니다.

- **URL**: `https://vault-in.hdel.co.kr:8070/api/getDutyMetaInfo`
- **HTTP Method**: `GET`
- **파라미터**:
  | 파라미터명 | 타입 | 필수 여부 | 설정값 | 설명 |
  |---|---|---|---|---|
  | `key` | String | 필수 | `subae` | API 접근 인증 키 |

- **호출 예시**:
  ```text
  GET https://vault-in.hdel.co.kr:8070/api/getDutyMetaInfo?key=subae
  ```