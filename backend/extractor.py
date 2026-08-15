"""
Stage 2: for each scraped scheme, download its guideline PDF, extract the
raw text, and ask Gemini to pull out structured eligibility fields matching
our schemes.json schema. This is LLM-assisted structured extraction —
using the LLM not to answer a question, but to convert messy unstructured
text into a strict, predictable JSON shape.

IMPORTANT: this writes to a SEPARATE file (scraped_schemes_extracted.json),
not directly into schemes.json. LLM extraction can make mistakes on messy
government PDFs, and this data will inform what real students see — it
needs a human (you) to review it before it's trusted, same principle as
why the rule engine never lets the LLM decide eligibility outcomes.
"""
import json
import io
import re
import time
import requests
from pypdf import PdfReader
from google import genai
from google.genai import types
from dotenv import load_dotenv
import os

load_dotenv()
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

EXTRACTION_PROMPT_TEMPLATE = """You are extracting structured data from an Indian government
scholarship scheme guideline document. Read the text below and return ONLY a single JSON object
(no markdown fences, no explanation) with exactly these fields:

{{
  "scheme_id": "short-kebab-case-id-based-on-name",
  "name": "full scheme name",
  "ministry": "issuing ministry/department, or null if not stated",
  "category": ["list of eligible categories, e.g. General, SC, ST, OBC, EWS, Minority, DNT — use [] if not category-restricted"],
  "education_level": ["list from: class9, class10, class11, class12, diploma, undergraduate, postgraduate, masters, phd, technical, professional — best guess from context"],
  "income_limit_inr": <number, the annual family/parental income ceiling in INR, or null if none stated>,
  "gender": "female" or "male" or "any",
  "states": ["ALL"] unless the scheme is restricted to specific states, then list them,
  "benefit": "short description of the monetary benefit/amount",
  "deadline": "deadline info if stated, else 'Check NSP for current dates'",
  "documents_required": ["list of documents mentioned, best effort"],
  "description": "2-3 sentence plain-English summary of who this is for and the key eligibility criteria"
}}

Only use facts actually present in the text below. If a field truly cannot be determined, use null
(or [] for list fields). Do not guess numbers that aren't stated.

SCHEME NAME: {scheme_name}

DOCUMENT TEXT:
{pdf_text}
"""


def extract_pdf_text(pdf_url: str, max_chars: int = 8000) -> str | None:
    try:
        resp = requests.get(pdf_url, timeout=30, headers={"User-Agent": "Mozilla/5.0"})
        resp.raise_for_status()
        reader = PdfReader(io.BytesIO(resp.content))
        text = ""
        for page in reader.pages:
            text += (page.extract_text() or "") + "\n"
            if len(text) > max_chars:
                break
        return text[:max_chars]
    except Exception as e:
        print(f"   [!] Failed to fetch/parse PDF: {e}")
        return None

def extract_structured_data(scheme_name: str, pdf_text: str, max_retries: int = 3) -> dict | None:
    prompt = EXTRACTION_PROMPT_TEMPLATE.format(scheme_name=scheme_name, pdf_text=pdf_text)

    for attempt in range(max_retries):
        try:
            print(f"   -> sending to Gemini ({len(pdf_text)} chars, attempt {attempt + 1})...")
            response = client.models.generate_content(
                model="gemini-flash-latest",
                contents=prompt,
                config=types.GenerateContentConfig(
                    http_options=types.HttpOptions(timeout=25000)  # 25 seconds, in milliseconds
                ),
            )
            raw = response.text.strip()
            raw = re.sub(r"^```(json)?|```$", "", raw.strip(), flags=re.MULTILINE).strip()
            return json.loads(raw)
        except Exception as e:
            wait = 2 ** attempt
            print(f"   [!] Attempt {attempt + 1} failed ({e}), retrying in {wait}s...")
            time.sleep(wait)

    print(f"   [!] Giving up on '{scheme_name}' after {max_retries} attempts.")
    return None


if __name__ == "__main__":
    with open("scraped_scheme_links.json", "r") as f:
        scheme_links = json.load(f)

    results = []

    def save_progress():
        with open("scraped_schemes_extracted.json", "w") as f:
            json.dump(results, f, indent=2)

    for i, item in enumerate(scheme_links):
        if not item.get("guideline_pdf") or item["guideline_pdf"] == "null" or "null" in item["guideline_pdf"]:
            print(f"[{i+1}/{len(scheme_links)}] Skipping (no valid PDF link): {item['name']}")
            continue

        print(f"[{i+1}/{len(scheme_links)}] Processing: {item['name']}")
        pdf_text = extract_pdf_text(item["guideline_pdf"])
        if not pdf_text:
            continue

        data = extract_structured_data(item["name"], pdf_text)
        if data:
            data["apply_link"] = "https://scholarships.gov.in"
            data["source_pdf"] = item["guideline_pdf"]
            results.append(data)
            print(f"   -> extracted OK ({data.get('scheme_id')})")
            save_progress()  # write to disk after EVERY success, not just at the end
        time.sleep(2)

    print(f"\nDone. {len(results)}/{len(scheme_links)} schemes extracted.")
    print("Saved to scraped_schemes_extracted.json — REVIEW THIS before merging into schemes.json.")