import urllib.request
import ssl
import json
import csv
import os

def main():
    url = 'https://vault-in.hdel.co.kr:8070/api/getCodeList?key=subae'
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE

    print("Fetching data from API...")
    req = urllib.request.urlopen(url, context=ctx)
    content = req.read().decode('utf-8')
    data = json.loads(content)

    print(f"Total rows fetched: {len(data)}")

    output_dir = os.path.join(os.getcwd(), 'reference')
    os.makedirs(output_dir, exist_ok=True)
    output_path = os.path.join(output_dir, '엘리베이터_특성코드.csv')

    fieldnames = ['code', 'codeName', 'typeName', 'typeVal', 'name']

    with open(output_path, 'w', newline='', encoding='utf-8-sig') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for row in data:
            # Filter row to only contain expected fieldnames
            filtered_row = {k: row.get(k, '') for k in fieldnames}
            writer.writerow(filtered_row)

    print(f"Successfully saved to: {output_path}")

if __name__ == '__main__':
    main()
