import requests

url = "http://127.0.0.1:8888/search"
params = {"q": "test"}

try:
    resp = requests.get(url, params=params, timeout=5)
    print(f"Status: {resp.status_code}")
    with open("search_results.html", "w", encoding="utf-8") as f:
        f.write(resp.text)
except Exception as e:
    print(f"Error: {e}")
