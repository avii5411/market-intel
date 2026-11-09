import json
import os
import time
from typing import Optional

from dotenv import load_dotenv
from google import genai
from pydantic import BaseModel

from fetch import fetch_page_text
from search import search_web

load_dotenv()

MODEL = "gemini-3.8-flash"
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))


class Company(BaseModel):
    name: str
    country: Optional[str]
    product: Optional[str]
    funding_or_contract: Optional[str]
    known_customers: list[str]
    evidence: Optional[str]


class Extraction(BaseModel):
    companies: list[Company]


PROMPT = """You are a market research analyst. From the TEXT below, extract
every company that makes or supplies counter-drone / drone-detection products.

Rules:
- Use ONLY information stated in the text. Never use outside knowledge.
- If a field is not stated in the text, use null (or an empty list).
- "evidence" is one short sentence, in your own words, showing where
  the text mentions this company.
- If the text names no such companies, return an empty list.
"""


def call_gemini(contents, retries=5):
    """Call Gemini, waiting and retrying when the service is busy."""
    for attempt in range(1, retries + 1):
        try:
            return client.models.generate_content(
                model=MODEL,
                contents=contents,
                config={
                    "response_mime_type": "application/json",
                    "response_schema": Extraction,
                },
            )
        except Exception as error:
            message = str(error)
            daily_limit = "PerDay" in message
            temporary = ("503" in message or "429" in message) and not daily_limit
            if not temporary or attempt == retries:
                raise
            wait = 10 * attempt
            print(f"    Gemini busy, retrying in {wait}s ({attempt}/{retries})")
            time.sleep(wait)


def extract_companies(text, source_url):
    """Ask Gemini for structured company data. Returns a list of dicts."""
    response = call_gemini(PROMPT + "\n\nTEXT:\n" + text[:20000])

    data = response.parsed
    if data is None:
        return []

    rows = []
    for company in data.companies:
        row = company.model_dump()
        row["source_url"] = source_url
        rows.append(row)
    return rows


if __name__ == "__main__":
    results = search_web("counter-drone detection systems Poland")

    for r in results[:3]:
        print(f"Reading: {r['title']}")
        text = fetch_page_text(r["href"])
        if not text:
            continue
        rows = extract_companies(text, r["href"])
        print(json.dumps(rows, indent=2, ensure_ascii=False))
        print()
        time.sleep(2)