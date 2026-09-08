import json
import urllib.parse
import urllib.request
import ssl

API_URL = "https://vault-in.hdel.co.kr:8070/api/executeQuery"
API_KEY = "subae"

def test_query(sql):
    query_string = urllib.parse.urlencode({"key": API_KEY, "sql": sql})
    url = f"{API_URL}?{query_string}"
    req = urllib.request.Request(url, headers={"Accept": "application/json"})
    context = ssl._create_unverified_context()
    with urllib.request.urlopen(req, context=context) as resp:
        data = json.loads(resp.read().decode('utf-8'))
        return data

# 전체 BLOCKNO$SF 의 MD$NUMBER 가져오기
blocks = test_query("SELECT MD$NUMBER FROM HDEL_DEFAULT.BLOCKNO$SF")
print(f"Total blocks in SF: {len(blocks)}")

matching_b181 = [b['MD$NUMBER'] for b in blocks if '181' in str(b.get('MD$NUMBER', ''))]
print("Matching 181 blocks:", matching_b181)

matching_b = [b['MD$NUMBER'] for b in blocks if str(b.get('MD$NUMBER', '')).startswith('B')]
print(f"Blocks starting with B count: {len(matching_b)}")
print("Sample B blocks:", matching_b[:20])
