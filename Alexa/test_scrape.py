import re

def _scrape_searxng_html(html_content: str) -> list:
    results = []
    # Find all article blocks
    articles = re.findall(r'<article class="result result-default category-general">(.*?)</article>', html_content, re.DOTALL)
    
    print(f"Found {len(articles)} articles")
    
    for article in articles:
        # Title
        title_match = re.search(r'<h3><a href="[^"]*"[^>]*>(.*?)</a></h3>', article, re.DOTALL)
        title = title_match.group(1) if title_match else ""
        # Remove HTML tags from title
        title = re.sub(r'<[^>]+>', '', title).strip()
        
        # URL
        # The first href in the article is usually the url_header
        url_match = re.search(r'href="([^"]*)"', article)
        url = url_match.group(1) if url_match else ""
        
        # Content
        content_match = re.search(r'<p class="content">(.*?)</p>', article, re.DOTALL)
        content = content_match.group(1) if content_match else ""
        # Remove HTML tags from content
        content = re.sub(r'<[^>]+>', '', content).strip()
        
        if title and url:
            results.append({
                "title": title,
                "url": url,
                "content": content
            })
            
    return results

with open("search_results.html", "r", encoding="utf-8") as f:
    html = f.read()
    
results = _scrape_searxng_html(html)
for res in results[:3]:
    print(res)
