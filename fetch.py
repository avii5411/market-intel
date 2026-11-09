import requests
import trafilatura

from search import search_web

HEADERS = {"User-Agent": "Mozilla/5.0 (compatible; MarketIntelDemo/0.1)"}


def fetch_page_text(url, timeout=15):
    """Download a page and return its main text, or None if it fails."""
    try:
        response = requests.get(url, headers=HEADERS, timeout=timeout)
        response.raise_for_status()
    except requests.RequestException as error:
        print(f"  FAILED: {url} ({error})")
        return None

    return trafilatura.extract(response.content)


if __name__ == "__main__":
    results = search_web("counter-drone detection systems Poland")

    if not results:
        print("No results found, wait for a few minutes and try again.")
        raise SystemExit

    for r in results:
        print(r["title"])
        text = fetch_page_text(r["href"])
        if text:
            print(f"  OK: {len(text)} characters")
            print(f"  Preview: {text[:200]}")
        print()