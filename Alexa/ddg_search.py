from ddgs import DDGS

with DDGS() as ddgs:
    results = ddgs.text("ESP32 WLED PCB design tips", max_results=5)
    
    for r in results:
        print(r["title"])
        print(r["href"])
        print(r["body"])
        print("-" * 50)
