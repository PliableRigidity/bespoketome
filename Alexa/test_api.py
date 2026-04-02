"""
Quick API test - tests the /api/chat endpoint directly
"""
import requests
import json

print("="*70)
print("TESTING JARVIS API")
print("="*70)

url = "http://localhost:5000/api/chat"

# Test 1: Simple query
print("\n[TEST 1] Simple query: 'hello'")
response = requests.post(url, json={"message": "hello"})
data = response.json()
print(f"Status: {response.status_code}")
print(f"Response type: {type(data.get('response'))}")
if isinstance(data.get('response'), dict):
    print(f"Text: {data['response'].get('text', '')[:100]}...")
    print(f"Images: {len(data['response'].get('images', []))} images")
    print(f"Sources: {len(data['response'].get('sources', []))} sources")
else:
    print(f"Response: {str(data.get('response'))[:100]}...")

# Test 2: Image query
print("\n[TEST 2] Image query: 'show me a cat'")
response = requests.post(url, json={"message": "show me a cat"})
data = response.json()
print(f"Status: {response.status_code}")
if isinstance(data.get('response'), dict):
    print(f"Text: {data['response'].get('text', '')[:100]}...")
    images = data['response'].get('images', [])
    print(f"Images: {len(images)} images")
    if images:
        print(f"  First image: {images[0].get('title', 'No title')}")
        print(f"  URL: {images[0].get('image_url', '')[:60]}...")
else:
    print(f"Response: {str(data.get('response'))[:100]}...")

# Test 3: Web search query
print("\n[TEST 3] Web search: 'what is python'")
response = requests.post(url, json={"message": "what is python"})
data = response.json()
print(f"Status: {response.status_code}")
if isinstance(data.get('response'), dict):
    print(f"Text: {data['response'].get('text', '')[:150]}...")
    sources = data['response'].get('sources', [])
    print(f"Sources: {len(sources)} sources")
    if sources:
        print(f"  First source: {sources[0].get('title', 'No title')}")
        print(f"  URL: {sources[0].get('url', '')[:60]}...")
else:
    print(f"Response: {str(data.get('response'))[:100]}...")

print("\n" + "="*70)
print("API TEST COMPLETE")
print("="*70)
