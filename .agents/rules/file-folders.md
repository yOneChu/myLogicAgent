---
trigger: always_on
---

## 기본 규칙

- 가상환경은 반드시 uv만 사용합니다. 
- 가상환경은 워크스페이스 루트의 .venv 하나만 사용합니다.
- 새 프로젝트 폴더를 만들어도 별도 가상환경을 만들지 말고 공통 .venv를 사용합니다.
- .venv가 이미 있으면 다시 생성하지 않습니다.
- 새 프로젝트 폴더를 만들면 내부에 images, docs, src, data 폴더를 자동으로 생성합니다.
- images는 시각화 이미지 저장, docs는 문서 저장, src는 코드 파일 저장, data는 데이터 파일 저장 용도로 사용합니다.
- 모든 패키지 설치와 실행은 uv 기준으로 진행합니다.
- conda, poetry, pipenv, virtualenv, python -m venv는 사용하지 않습니다.

기본 구조 예시

workspace/
  .venv/
  project-a/
    images/
    docs/
    src/
    data/
  project-b/
    images/
    docs/
    src/
    data/

새 프로젝트 생성 요청 시에는 다음 원칙으로 작업합니다.
- 워크스페이스 루트의 .venv 존재 여부를 확인합니다.
- 없으면 uv로 .venv를 생성합니다.
- 지정한 프로젝트 폴더와 그 안의 images, docs, src, data 폴더를 생성합니다.
- 이후 작업은 모두 공통 .venv를 기준으로 진행합니다.


## 추가 사항
- LLM을 통해 쿼리 실행 및 PLM API 수행하는 결과는 /script/db_query 폴더 안의 'query_to_csv.py' , 'query_to_excel.py'을 통해 csv와 excel파일을 생성한다.  조회 쿼리를 작성하고 실행 결과를 CSV 또는 Excel(xlsx) 파일로 생성할 때 따라야 할 공통 규칙을 정의한다.


---

| 구분 | 경로 | 용도 |
|---|---|---|
| CSV 출력 폴더 | `output_csv` | 생성된 CSV 파일 저장 위치 |
| Excel 출력 폴더 | `output_excel` | 생성된 Excel 파일 저장 위치 (스크립트가 자동 생성) |