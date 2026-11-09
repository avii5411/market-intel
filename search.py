import hashlib
import json
import time
from pathlib import Path

from ddgs import DDGS

CACHE_DIR = Path("cache")
CACHE_DIR.mkdir(exist_ok=True)


def search_web(query, max_results=10, retries=3):
    """Search the web. Uses a saved copy if we searched this before."""
    name = hashlib.md5(query.encode()).hexdigest() + ".json"
    cache_file = CACHE_DIR / name

    if cache_file.exists():
        return json.loads(cache_file.read_text(encoding="utf-8"))

    for attempt in range(1, retries + 1):
        try:
            with DDGS() as ddgs:
                results = list(ddgs.text(query, max_results=max_results))
            if results:
                cache_file.write_text(
                    json.dumps(results, ensure_ascii=False), encoding="utf-8"
                )
                return results
        except Exception as error:
            print(f"  Search attempt {attempt} failed: {error}")
        time.sleep(3 * attempt)

    return []


if __name__ == "__main__":
    results = search_web("counter-drone detection systems Poland")
    for i, r in enumerate(results, start=1):
        print(f"{i}. {r['title']}")
        print(f"   {r['href']}")
        print()