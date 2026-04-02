import os

class DummyCache:
    """Simple in-memory cache when diskcache is missing."""
    def __init__(self, *args, **kwargs):
        self._store = {}
        
    def get(self, key):
        return self._store.get(key)
        
    def set(self, key, value, expire=None):
        self._store[key] = value

try:
    import diskcache
    _HAS_DISKCACHE = True
except ImportError:
    _HAS_DISKCACHE = False

# Cache location (relative to project root or in a standard temp loc)
CACHE_DIR = os.path.join(os.path.dirname(__file__), "..", ".cache", "web_retrieval")

if _HAS_DISKCACHE:
    # 60 mins for search results
    SEARCH_CACHE = diskcache.Cache(os.path.join(CACHE_DIR, "search"))
    # 12 hours for content extraction
    CONTENT_CACHE = diskcache.Cache(os.path.join(CACHE_DIR, "content"))
else:
    SEARCH_CACHE = DummyCache()
    CONTENT_CACHE = DummyCache()

def get_search_cache(key):
    return SEARCH_CACHE.get(key)

def set_search_cache(key, value, expire=3600):
    SEARCH_CACHE.set(key, value, expire=expire)

def get_content_cache(key):
    return CONTENT_CACHE.get(key)

def set_content_cache(key, value, expire=43200):
    CONTENT_CACHE.set(key, value, expire=expire)
