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

# Test HDEL_DEFAULT.HEXTODEC
print("HDEL_DEFAULT.HEXTODEC test:", test_query("SELECT HDEL_DEFAULT.HEXTODEC('8613724A') AS OUID FROM DUAL"))

# Test Join with HDEL_DEFAULT.HEXTODEC
sql_join = """
SELECT COUNT(DISTINCT NP.MD$NUMBER) AS PART_CNT
  FROM HDEL_DEFAULT.NORMALPART$VF NP
 WHERE (SELECT MD$NUMBER FROM HDEL_DEFAULT.BLOCKNO$SF
         WHERE SF$OUID = DECODE(NP.BLOCKNO, NULL, NULL, HDEL_DEFAULT.HEXTODEC(UPPER(SUBSTR(NP.BLOCKNO, 12))))) = 'B181B'
"""
print("Part Count for B181B via HDEL_DEFAULT.HEXTODEC:", test_query(sql_join))
