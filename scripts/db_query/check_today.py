import json
import ssl
import sys
import urllib.parse
import urllib.request
import pandas as pd


def execute_sql(sql: str) -> list:
    """
    SQL 쿼리를 실행하여 API 결과를 반환하는 함수
    :param sql: 실행할 SELECT SQL 문
    :param return: JSON 응답 데이터 (list)
    """
    url = "https://vault-in.hdel.co.kr:8070/api/executeQuery?" + urllib.parse.urlencode(
        {"key": "subae", "sql": sql}
    )
    ctx = ssl._create_unverified_context()
    req = urllib.request.Request(
        url, headers={"Accept": "application/json", "User-Agent": "dutyreview-checker"}
    )

    with urllib.request.urlopen(req, context=ctx, timeout=30) as res:
        raw = res.read()
        text = raw.decode("utf-8", errors="replace")
        return json.loads(text)


def main():
    sys.stdout.reconfigure(encoding="utf-8")

    # 1. 오늘 날짜(20260811) 기준 비표준 사양검토 등록 건 조회
    today_str = "20260811"
    print(f"=== [1] 오늘({today_str}) 등록된 비표준 사양검토 조회 ===")

    sql_today = f"""
    SELECT
        D.MD$NUMBER AS REQNO,
        D.MD$CDATE AS CDATE,
        D.MD$STATUS AS STATUS,
        D.REQTIME AS REQTIME,
        D.DUTYTITLE1 AS TITLE,
        HDEL_DEFAULT.CODN(D.DIVISION) AS DIVISION,
        HDEL_DEFAULT.CODN(D.SUJUSTAT) AS SUJUSTAT,
        D.SUJUNUM AS SUJUNUM,
        D.FILEDNAME AS FILEDNAME,
        D.PRODUCT_TYPE01 AS PRODUCT_TYPE01,
        HDEL_DEFAULT.CODN(D.PRODUCT_TYPE02) AS PRODUCT_TYPE02,
        HDEL_DEFAULT.CODN(D.WORKSCOPE) AS WORKSCOPE,
        D.REVIEWTITLE AS REVIEWTITLE,
        HDEL_DEFAULT.CODN(D.FIRST_TYPE) AS FIRST_TYPE,
        HDEL_DEFAULT.CODN(D.SECOND_TYPE) AS SECOND_TYPE,
        D.DETAIL AS DETAIL,
        D.MEMO AS MEMO,
        D.ACPTTIME AS ACPTTIME,
        D.FINTIME AS FINTIME,
        D.MANAGER AS MANAGER,
        HDEL_DEFAULT.CODN(D.STAT) AS STAT,
        HDEL_DEFAULT.CODN(D.NATION) AS NATION
    FROM HDEL_DEFAULT.dutyreview$sf D
    WHERE SUBSTR(D.MD$CDATE, 1, 8) = '{today_str}'
    ORDER BY D.MD$CDATE DESC
    """

    data_today = execute_sql(sql_today)
    print(f"오늘({today_str}) 등록된 건수: {len(data_today)}건\n")

    # 2. 최근 등록된 비표준 사양검토 전체 데이터 및 최신 날짜 확인 (상위 50건)
    print("=== [2] 최근 등록된 비표준 사양검토 목록 (상위 50건) ===")
    sql_recent = """
    SELECT * FROM (
        SELECT
            D.MD$NUMBER AS REQNO,
            D.MD$CDATE AS CDATE,
            D.MD$STATUS AS STATUS,
            D.REQTIME AS REQTIME,
            D.DUTYTITLE1 AS TITLE,
            HDEL_DEFAULT.CODN(D.DIVISION) AS DIVISION,
            HDEL_DEFAULT.CODN(D.SUJUSTAT) AS SUJUSTAT,
            D.SUJUNUM AS SUJUNUM,
            D.FILEDNAME AS FILEDNAME,
            D.PRODUCT_TYPE01 AS PRODUCT_TYPE01,
            HDEL_DEFAULT.CODN(D.PRODUCT_TYPE02) AS PRODUCT_TYPE02,
            HDEL_DEFAULT.CODN(D.WORKSCOPE) AS WORKSCOPE,
            D.REVIEWTITLE AS REVIEWTITLE,
            HDEL_DEFAULT.CODN(D.FIRST_TYPE) AS FIRST_TYPE,
            HDEL_DEFAULT.CODN(D.SECOND_TYPE) AS SECOND_TYPE,
            D.DETAIL AS DETAIL,
            D.MEMO AS MEMO,
            D.ACPTTIME AS ACPTTIME,
            D.FINTIME AS FINTIME,
            D.MANAGER AS MANAGER,
            HDEL_DEFAULT.CODN(D.STAT) AS STAT,
            HDEL_DEFAULT.CODN(D.NATION) AS NATION
        FROM HDEL_DEFAULT.dutyreview$sf D
        ORDER BY D.MD$CDATE DESC
    ) WHERE ROWNUM <= 50
    """

    data_recent = execute_sql(sql_recent)
    print(f"최근 조회 건수: {len(data_recent)}건")

    if data_recent:
        df = pd.DataFrame(data_recent)
        print("최신 등록일자 Top 10:")
        print(df[["REQNO", "CDATE", "STAT", "DIVISION", "FILEDNAME", "MANAGER"]].head(10))

        # 등록일자 분포 확인
        df["CDATE_DATE"] = df["CDATE"].astype(str).str.slice(0, 8)
        print("\n최근 50건의 등록일자별 건수:")
        print(df["CDATE_DATE"].value_counts().sort_index(ascending=False))

    # 3. 오늘(20260811) 의뢰일(REQTIME), 접수일(ACPTTIME), 완료일(FINTIME) 기준 변경/진행 건 확인
    sql_today_activity = f"""
    SELECT
        D.MD$NUMBER AS REQNO,
        D.MD$CDATE AS CDATE,
        D.REQTIME AS REQTIME,
        D.ACPTTIME AS ACPTTIME,
        D.FINTIME AS FINTIME,
        HDEL_DEFAULT.CODN(D.STAT) AS STAT,
        D.FILEDNAME AS FILEDNAME,
        D.MANAGER AS MANAGER
    FROM HDEL_DEFAULT.dutyreview$sf D
    WHERE SUBSTR(D.MD$CDATE, 1, 8) = '{today_str}'
       OR SUBSTR(D.REQTIME, 1, 8) = '{today_str}'
       OR SUBSTR(D.ACPTTIME, 1, 8) = '{today_str}'
       OR SUBSTR(D.FINTIME, 1, 8) = '{today_str}'
    """
    data_act = execute_sql(sql_today_activity)
    print(f"\n=== [3] 오늘({today_str}) 활동(등록/의뢰/접수/완료) 건수: {len(data_act)}건 ===")
    if data_act:
        print(pd.DataFrame(data_act))


if __name__ == "__main__":
    main()
