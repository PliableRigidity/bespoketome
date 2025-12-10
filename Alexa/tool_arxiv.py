import requests
import xml.etree.ElementTree as ET

def search_arxiv(query: str, max_results: int = 5) -> str:
    """
    Search ArXiv for academic papers.
    Returns a formatted string with paper titles, authors, and summaries.
    """
    base_url = "http://export.arxiv.org/api/query"
    
    # Clean query
    query = query.replace(" ", "+")
    
    params = {
        "search_query": f"all:{query}",
        "start": 0,
        "max_results": max_results,
        "sortBy": "relevance",
        "sortOrder": "descending"
    }
    
    try:
        response = requests.get(base_url, params=params, timeout=15)
        response.raise_for_status()
        
        # Parse XML response
        root = ET.fromstring(response.content)
        
        # ArXiv API uses Atom namespace
        ns = {'atom': 'http://www.w3.org/2005/Atom'}
        
        entries = root.findall('atom:entry', ns)
        
        if not entries:
            return "I couldn't find any papers matching that query."
            
        result_text = f"Here are the top {len(entries)} ArXiv papers for '{query.replace('+', ' ')}':\n\n"
        
        for i, entry in enumerate(entries):
            title = entry.find('atom:title', ns).text.strip().replace('\n', ' ')
            summary = entry.find('atom:summary', ns).text.strip().replace('\n', ' ')
            published = entry.find('atom:published', ns).text[:10]
            link = entry.find('atom:id', ns).text
            
            # Get authors
            authors = []
            for author in entry.findall('atom:author', ns):
                name = author.find('atom:name', ns).text
                authors.append(name)
            author_str = ", ".join(authors[:3]) # First 3 authors
            if len(authors) > 3:
                author_str += " et al."
                
            result_text += f"**{i+1}. {title}**\n"
            result_text += f"*Authors:* {author_str} ({published})\n"
            result_text += f"*Link:* {link}\n"
            result_text += f"*Summary:* {summary[:300]}...\n\n"
            
        return result_text
        
    except Exception as e:
        return f"Error searching ArXiv: {str(e)}"
