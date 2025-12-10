import requests

url = "http://localhost:8888"
search_url = f"{url}/search"

print(f"Testing connection to {url}...")
try:
    # Test 1: Root URL
    resp = requests.get(url, timeout=5)
    print(f"Root URL Status: {resp.status_code}")
except Exception as e:
    print(f"Root URL failed: {e}")

print("\nTesting JSON search...")
try:
    # Test 2: JSON Search
    params = {"q": "test", "format": "json"}
    # Try with no headers first
    resp = requests.get(search_url, params=params, timeout=5)
    print(f"JSON Search (no headers) Status: {resp.status_code}")
    if resp.status_code == 403:
        print(f"Response text: {resp.text}")
        
    # Try with headers
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36"
    }
    
    for fmt in ["json", "csv", "rss"]:
        print(f"\nTesting {fmt.upper()} format...")
        params = {"q": "test", "format": fmt}
        resp = requests.get(search_url, params=params, headers=headers, timeout=5)
        print(f"{fmt.upper()} Status: {resp.status_code}")
        if resp.status_code == 403:
            print(f"Response text: {resp.text}")
    
except Exception as e:
    print(f"Search failed: {e}")
