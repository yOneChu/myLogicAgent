---
trigger: always_on
---

# 01. 로직 정합성 작성/수정 규칙
- 정합성 로직 PID는 'BOM_'로 시작한다.
- 'BOM_부품의블럭번호' 이다. (ex. BOM_E321A)
- 정합성 PID의 'FUNCTION_READ_BOM'를 CALL하면 해당 현장의 모든 속성값, 주석값 등 들을 가져온다.
- SPEC: 'E321A_PNO' , CON: '!N' 은 E321A 블럭넘버에 해당하는 자재가 수배되었다는 것이다.
- '!N'은 값이 공백이 아니라는 것이다.


## 예시
- 'BOM_E321A'의 주석정보를 가져오려면 'KEY: CALL, VAL : FUNCTION_READ_BOM'을 선언하면 해당 현장(호기)의 모든 부품의 정보를 가져온다.


```
E321A_CMT : 주석
E321A_PNO : 자재(부품) 번호
E321A_SPE : 자재(부품) SPEC

```