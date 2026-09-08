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

# 1. HEXTODEC('8613724A') 테스트
print("HEXTODEC test:", test_query("SELECT HEXTODEC('8613724A') AS DEC_VAL FROM DUAL"))

# 2. TO_NUMBER test
print("TO_NUMBER test:", test_query("SELECT TO_NUMBER('8613724A', 'XXXXXXXX') AS DEC_VAL FROM DUAL"))

# 3. SF$OUID comparison test
print("OUID eq test 1:", test_query("SELECT SF$OUID, MD$NUMBER FROM HDEL_DEFAULT.BLOCKNO$SF WHERE SF$OUID = HEXTODEC('8613724A')"))
print("OUID eq test 2:", test_query("SELECT SF$OUID, MD$NUMBER FROM HDEL_DEFAULT.BLOCKNO$SF WHERE TO_CHAR(SF$OUID) = TO_CHAR(HEXTODEC('8613724A'))"))
print("OUID eq test 3:", test_query("SELECT SF$OUID, MD$NUMBER FROM HDEL_DEFAULT.BLOCKNO$SF WHERE SF$OUID = 2249486922"))

# 4. SUBSTR check on NP.BLOCKNO
sql_substr = """
SELECT NP.MD$NUMBER, NP.BLOCKNO, SUBSTR(NP.BLOCKNO, 12) AS SUB12, HEXTODEC(UPPER(SUBSTR(NP.BLOCKNO, 12))) AS DEC_OUID
  FROM HDEL_DEFAULT.NORMALPART$VF NP
 WHERE NP.BLOCKNO LIKE '%8613724a%'
"""
print("SUBSTR test:", test_query(sql_substr))
