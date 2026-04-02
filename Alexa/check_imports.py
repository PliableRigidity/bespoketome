
try:
    import duckduckgo_search
    print("duckduckgo_search imported successfully")
except ImportError:
    print("duckduckgo_search not found")

try:
    import ddgs
    print("ddgs imported successfully")
except ImportError:
    print("ddgs not found")

try:
    from duckduckgo_search import DDGS
    print("DDGS imported from duckduckgo_search")
except ImportError:
    print("DDGS not found in duckduckgo_search")

try:
    from ddgs import DDGS
    print("DDGS imported from ddgs")
except ImportError:
    print("DDGS not found in ddgs")
