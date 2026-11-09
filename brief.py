from datetime import date

import pandas as pd
from docx import Document
from docx.shared import Inches, Pt

TOPIC = "Counter-drone detection in Poland"


def load_table(filename="market_intel.xlsx"):
    """Read the Excel table and replace empty cells with readable text."""
    df = pd.read_excel(filename)
    for column in ["country", "product", "funding_or_contract"]:
        df[column] = df[column].fillna("not stated")
    return df
def add_company_table(doc, df):
    """Add a table with one row per company."""
    headers = ["Company", "Country", "Product", "Sources", "Verify?"]
    table = doc.add_table(rows=1, cols=len(headers))
    table.style = "Light Grid Accent 1"

    for cell, header in zip(table.rows[0].cells, headers):
        cell.text = header

    for _, row in df.iterrows():
        cells = table.add_row().cells
        cells[0].text = str(row["company"])
        cells[1].text = str(row["country"])
        cells[2].text = str(row["product"])[:110]
        cells[3].text = str(row["mentions"])
        cells[4].text = str(row["needs_verification"])

def build_brief(df, filename="market_brief.docx"):
    """Create the one-page market brief as a Word file."""
    doc = Document()

    section = doc.sections[0]
    section.left_margin = section.right_margin = Inches(0.8)
    section.top_margin = section.bottom_margin = Inches(0.7)
    doc.styles["Normal"].font.size = Pt(10)

    doc.add_heading(f"Market Brief: {TOPIC}", level=1)
    doc.add_paragraph(f"Generated on {date.today():%d %B %Y} from public sources.")

    total = len(df)
    strong = int((df["mentions"] >= 2).sum())
    to_check = int((df["needs_verification"] == "Yes").sum())

    doc.add_heading("Summary", level=2)
    doc.add_paragraph(
        f"The pipeline identified {total} companies active in this market. "
        f"{strong} of them appear in two or more independent sources; "
        f"{to_check} are flagged for human verification."
    )

    doc.add_heading("Key players (most-cited first)", level=2)
    add_company_table(doc, df.head(8))

    doc.add_heading("Needs verification", level=2)
    flagged = df[df["needs_verification"] == "Yes"]["company"].tolist()
    doc.add_paragraph(", ".join(flagged) if flagged else "None.")

    doc.add_heading("Sources", level=2)
    urls = sorted({u for cell in df["sources"] for u in str(cell).split("\n")})
    for url in urls:
        doc.add_paragraph(url, style="List Bullet")

    doc.add_paragraph(
        "Note: generated automatically. Items flagged above rest on a single "
        "source or lack key facts and must be checked before external use."
    )
    doc.save(filename)


if __name__ == "__main__":
    table = load_table()
    build_brief(table)
    print(f"Brief saved: {len(table)} companies.")