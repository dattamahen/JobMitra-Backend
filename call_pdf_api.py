import urllib.request
import json

url = "http://localhost:8000/api/v1/resume/generate-pdf-test"
payload = json.dumps({"html": "<html><body><h1>Test PDF</h1></body></html>", "filename": "test"}).encode()
req = urllib.request.Request(url, data=payload, headers={"Content-Type": "application/json"}, method="POST")

try:
    with urllib.request.urlopen(req, timeout=60) as r:
        body = r.read()
        ct = r.headers.get("Content-Type", "")
        print(f"STATUS: 200")
        print(f"Content-Type: {ct}")
        print(f"Size: {len(body)} bytes")
        if b"%PDF" in body[:10]:
            print("RESULT: SUCCESS - valid PDF returned")
            with open("api_test_result.pdf", "wb") as f:
                f.write(body)
            print("Saved to api_test_result.pdf")
        else:
            print("RESULT: Got response but not a PDF:", body[:200])
except urllib.error.HTTPError as e:
    body = e.read().decode()
    print(f"STATUS: {e.code}")
    print(f"ERROR: {body}")
except Exception as e:
    print(f"EXCEPTION: {e}")
