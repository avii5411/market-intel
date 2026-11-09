# Market Intel Pipeline

A small Python project that turns a market topic into a **sourced competitor table** and a **one-page brief**, mostly on autopilot.

I'm a student and built this to learn how AI automation works in practice. I picked **counter-drone detection in {country}** as the test topic because it's a hot market and there's a lot of public info to work with.

## What it does

You give it search queries. It finds web pages, reads them, pulls out the companies it finds (name, country, product, contracts), merges everything into one table, and writes a short Word brief. Every row links back to the page it came from.

## How it works

```
search -> fetch -> extract -> merge -> generate
```

1. **Search** (`search.py`): finds URLs with DuckDuckGo. Results are cached so I don't get rate-limited.
2. **Fetch** (`fetch.py`): downloads each page and strips it down to the article text.
3. **Extract** (`extract.py`): sends the text to Gemini, which returns structured data (company, country, product, ...) in a fixed format.
4. **Merge** (`pipeline.py`): combines all pages into one table, removes duplicate companies, counts how many sources mention each one, and exports `market_intel.xlsx`.
5. **Generate** (`brief.py`): reads the Excel file and writes `market_brief.docx`.

`run_all.py` runs the pipeline and the brief in one go.

## How to run it

1. Install Python 3.11+ and create a virtual environment:
   ```
   py -m venv .venv
   .venv\Scripts\Activate.ps1
   ```
2. Install the libraries:
   ```
   pip install ddgs trafilatura requests pydantic pandas openpyxl python-docx python-dotenv google-genai
   ```
3. Get a free Gemini API key at [aistudio.google.com](https://aistudio.google.com) and put it in a file called `.env`:
   ```
   GEMINI_API_KEY=your_key_here
   ```
4. Run:
   ```
   python run_all.py
   ```

You'll get `market_intel.xlsx` and `market_brief.docx`. A sample brief is included in this repo. To try another topic, just change the `QUERIES` list in `pipeline.py`.

## Design decisions (the stuff I thought about)

- **The AI only does one job.** Gemini only turns messy text into structured data. Searching, downloading and merging are normal code, which makes it easier to trust and debug.
- **No guessing.** The prompt says to use only the text it's given. If something isn't stated (like a country), it stays empty instead of being made up.
- **Source URLs come from my code, not the AI.** LLMs can invent links, so the code attaches the real URL of the page it read.
- **Uncertain rows get flagged.** A company that appears in only one source, or has no country, is marked `needs_verification`. The brief says so too.
- **Caching.** Searches and extractions are saved to disk, so reruns are fast and don't waste API requests.
- **Numbers in the brief are calculated, not written by AI.** So they can be traced back to the table.

## Limitations (being honest)

- **Free-tier limits are tight.** Gemini's free tier allowed only about 20 requests per day for the model I used, so I couldn't process every page in one day. Caching helps, but coverage is limited.
- **Name matching is basic.** I normalize names with simple rules (for example "APS" and "Advanced Protection Systems"), plus a small manual alias list for things like Polish vs. English names. A bigger version would need fuzzy matching.
- **Only the first 20,000 characters of each page are read**, so companies mentioned later in long articles can be missed.
- **The AI can still misread things.** That's why the sources and verification flags are there. Results are a starting point for a human to check, not final truth.
- **Services fail.** Search throttling and Gemini overloads happened a lot while I built this, so most steps retry or skip gracefully.
- **Public data only.** I'd never put sensitive or confidential info into a public AI tool. For real use, a private or local model would make more sense.

## What I'd do next

- Add more markets and product niches.
- Better duplicate detection for company names.
- Export leads straight into a CRM.
- Generate one-pagers per company automatically.

## Built with

Python, Gemini API, pydantic, pandas, trafilatura, python-docx.

*Presenting to you by Sai Avinash, TUM*
