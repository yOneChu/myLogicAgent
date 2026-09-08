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

# HDEL_DEFAULT Schema Prefix 사용해보기
print("1. BLOCKNO$SF count:", test_query("SELECT COUNT(*) FROM BLOCKNO$SF"))
print("2. HDEL_DEFAULT.BLOCKNO$SF count:", test_query("SELECT COUNT(*) FROM HDEL_DEFAULT.BLOCKNO$SF"))
print("3. BLOCKNO$VF count:", test_query("SELECT COUNT(*) FROM BLOCKNO$VF"))
print("4. HDEL_DEFAULT.BLOCKNO$VF count:", test_query("SELECT COUNT(*) FROM HDEL_DEFAULT.BLOCKNO$VF"))
print("5. NORMALPART$VF count:", test_query("SELECT COUNT(*) FROM NORMALPART$VF WHERE ROWNUM <= 5"))
