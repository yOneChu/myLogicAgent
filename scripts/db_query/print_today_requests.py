import json
import urllib.request
import urllib.parse
import ssl
import sys

def main():
    sys.stdout.reconfigure(encoding='utf-8')
    with open('scripts/db_query/query.sql', 'r', encoding='utf-8') as f:
        sql = f.read()
    
    url = 'https://vault-in.hdel.co.kr:8070/api/executeQuery?' + urllib.parse.urlencode({'key': 'subae', 'sql': sql})
    ctx = ssl._create_unverified_context()
    req = urllib.request.Request(url, headers={'Accept': 'application/json', 'User-Agent': 'test'})
    res = urllib.request.urlopen(req, context=ctx)
    raw = res.read()
    
    text = raw.decode('utf-8', errors='replace')
    data = json.loads(text)
    
    print(f"총 {len(data)}건의 기계로직 전산화요청이 조회되었습니다.\n")
    for idx, row in enumerate(data, 1):
        reqno = row.get('REQNO', '')
        status = row.get('STATUS', '')
        part = row.get('DESIGNPART', '')
        uname = row.get('REQ_USER_NAME', '')
        uid = row.get('REQ_USER_ID', '')
        manager = row.get('MANAGER') or '미지정'
        hogi = row.get('HOGI') or '없음'
        rtype = row.get('REQ_TYPE') or '-'
        rcause = row.get('REQ_CAUSE') or '-'
        cdate = row.get('CRE_DATE', '')
        rdetail = row.get('REQ_DETAIL', '')
        adetail = row.get('ANS_DETAIL') or '미완료/처리중'

        print(f"=== [{idx}] 요청번호: {reqno} ===")
        print(f"- 상태: {status}")
        print(f"- 구분: {part}")
        print(f"- 등록자: {uname} (ID: {uid})")
        print(f"- 담당자: {manager}")
        print(f"- 대표호기: {hogi}")
        print(f"- 작업구분: {rtype}")
        print(f"- 요청사유: {rcause}")
        print(f"- 등록일시: {cdate}")
        print(f"- 요청내용:\n{rdetail}")
        print(f"- 작업내용: {adetail}")
        print("-" * 50)

if __name__ == '__main__':
    main()
