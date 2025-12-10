from tool_web import search_web

print("Testing search_web...")
try:
    result = search_web("latest ai news")
    print("Result:")
    print(result)
except Exception as e:
    print(f"Error: {e}")
