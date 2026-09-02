
# PLM BOM 및 부품 관련 API 명세서

이 문서는 PLM의 BOM 및 부품 관련 API 정보를 정의합니다.





## 01. 부품(자재)의 속성 정보 API

다수의 부품(자재번호)들의 속성정보를 조회한다.


### Endpoint
- POST 방식
```
https://vault-in.hdel.co.kr:8070/api/findPartInfoWithList
```

### Request Parameters

- 여러 자재번호(품번)들을 ','를 구분기호로 연결해서 API에 전달한다. 

| 파라미터 | 타입 | 필수 | 값 | 설명 |
|---|---|---|---|---|
| `key` | string | Y | `subae` | 구분 키 |
| `PartNoList` | string | Y | `부품번호1,부품번호2,부품번호3` | 자재번호(품번)들 |


### Response Columns

- 반환갑은 List 형식에 부품의 객체가 담겨져 있다.
- 형식: ArrayList< 부품(자재) 객체 >
- 부품(자재) 객체의 속성(컬럼)은 아래와 같다.

| 부품(자재) 컬럼명 | 설명 |
|---|---|
| `partNo` | 부품(자재) 번호 |
| `partName` | 자재명 |
| `version` | 자재의 버전 |
| `nation` | 자재코드 Ownership |
| `desc` | name |
| `glCode` | GL_CODE |
| `spec` | spec |
| `uom` | 단위 |
| `partSize` | partSize |
| `originDiv` | 품목 |
| `cost` | 견적사용 |
| `design` | 설계사용 |


---
