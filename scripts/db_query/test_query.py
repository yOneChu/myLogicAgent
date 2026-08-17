"""
API 응답 결과 확인 및 디버깅용 스크립트.
주요 함수:
    debug_query(): API를 호출하여 반환된 JSON 원본 데이터를 확인한다.
"""

import json
import ssl
from urllib.parse import urlencode
from urllib.request import Request, urlopen

API_URL = "https://vault-in.hdel.co.kr:8070/api/executeQuery"
API_KEY = "subae"

def debug_query(sql: str) -> None:
    """
    SQL 쿼리를 실행하고 결과를 출력하는 함수.

    Args:
        sql (str): 실행할 SELECT SQL 문장
    """
    query_string = urlencode({"key": API_KEY, "sql": sql})
    url = f"{API_URL}?{query_string}"

    req = Request(
        url,
        method="GET",
        headers={
            "Accept": "application/json",
            "User-Agent": "debug-script/1.0",
        },
    )

    context = ssl._create_unverified_context()

    with urlopen(req, timeout=120, context=context) as response:
        raw_body = response.read()

    body = raw_body.decode("utf-8", errors="replace")
    print("=== Response Raw Body ===")
    print(body[:2000])

if __name__ == "__main__":
    with open("scripts/db_query/query_check_kim.sql", "r", encoding="utf-8") as f:
        sql_content = f.read().strip()
    debug_query(sql_content)
