import hashlib
import json
import time
from pathlib import Path

import pandas as pd

from extract import extract_companies
from fetch import fetch_page_text
from search import search_web

QUERIES = [
    "counter-drone detection systems Poland",
    "Polish SAN counter-drone program suppliers",
    "anti-drone radar acoustic detection Poland companies",
]
RESULTS_PER_QUERY = 4
CACHE_DIR = Path("cache")


def extract_cached(url):
    """Fetch and extract one page, saving the result so we never repeat it."""
    name = "extract_" + hashlib.md5(url.encode()).hexdigest() + ".json"
    cache_file = CACHE_DIR / name

    if cache_file.exists():
        return json.loads(cache_file.read_text(encoding="utf-8"))

    text = fetch_page_text(url)
    if not text:
        return []

    rows = extract_companies(text, url)
    cache_file.write_text(json.dumps(rows, ensure_ascii=False), encoding="utf-8")
    time.sleep(2)
    return rows
def collect_rows():
    """Run every query, read every page, return all extracted rows."""
    all_rows = []
    seen_urls = set()

    for query in QUERIES:
        print(f"Searching: {query}")
        results = search_web(query)

        for r in results[:RESULTS_PER_QUERY]:
            url = r["href"]
            if url in seen_urls:
                continue
            seen_urls.add(url)

            print(f"  Reading: {r['title']}")
            try:
                all_rows.extend(extract_cached(url))
            except Exception as error:
                print(f"    Skipped: {error}")

    return all_rows
def first_value(series):
    """Return the first non-empty value in a column, or None."""
    values = series.dropna()
    return values.iloc[0] if len(values) else None


def join_unique(lists):
    """Merge several lists into one sorted, comma-separated text."""
    items = sorted({item for sub in lists for item in sub})
    return ", ".join(items)


def build_table(rows):
    """Merge rows so there is one row per company."""
    df = pd.DataFrame(rows)
    df["key"] = df["name"].str.lower().str.strip()

    table = df.groupby("key").agg(
        company=("name", "first"),
        country=("country", first_value),
        product=("product", first_value),
        funding_or_contract=("funding_or_contract", first_value),
        known_customers=("known_customers", join_unique),
        mentions=("source_url", "nunique"),
        sources=("source_url", lambda s: "\n".join(sorted(set(s)))),
    )
    table = table.reset_index(drop=True)

    table["needs_verification"] = table.apply(
        lambda row: "Yes" if row["mentions"] < 2 or pd.isna(row["country"]) else "No",
        axis=1,
    )
    return table.sort_values("mentions", ascending=False)
def save_excel(table, filename="market_intel.xlsx"):
    """Write the table to Excel with readable column widths."""
    with pd.ExcelWriter(filename, engine="openpyxl") as writer:
        table.to_excel(writer, index=False, sheet_name="Competitors")
        sheet = writer.sheets["Competitors"]
        for column in sheet.columns:
            letter = column[0].column_letter
            sheet.column_dimensions[letter].width = 35


if __name__ == "__main__":
    rows = collect_rows()
    if not rows:
        print("No companies extracted. Check your searches and try again.")
        raise SystemExit

    table = build_table(rows)
    save_excel(table)
    print(f"\nDone: {len(table)} companies saved to market_intel.xlsx")
    print(table[["company", "country", "mentions", "needs_verification"]])