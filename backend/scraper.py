"""
Stage 1: scrape the scheme listing page for scheme names + links to their
official guideline PDFs. We deliberately anchor the scraping logic on the
"Specifications" link text rather than CSS classes/ids, since government
site markup changes without notice and link text is the most stable thing
to search for.
"""
import requests
from bs4 import BeautifulSoup
import json

BASE = "https://scholarships.gov.in"
LISTING_URL = f"{BASE}/All-Scholarships"


def fetch_scheme_list():
    resp = requests.get(LISTING_URL, timeout=30, headers={"User-Agent": "Mozilla/5.0"})
    resp.raise_for_status()
    soup = BeautifulSoup(resp.text, "html.parser")

    schemes = []
    seen_urls = set()

    # Every scheme card has a "Specifications" link pointing to its guideline PDF
    for link in soup.find_all("a"):
        text = link.get_text(strip=True)
        if "Specification" not in text:
            continue

        pdf_url = link.get("href")
        if not pdf_url or pdf_url in seen_urls:
            continue
        if pdf_url.startswith("/"):
            pdf_url = BASE + pdf_url
        seen_urls.add(pdf_url)

        # Walk backwards to find the nearest heading before this link — that's the scheme name
        heading = link.find_previous(["h6", "h5", "h4", "h3"])
        name = heading.get_text(strip=True) if heading else "UNKNOWN"

        schemes.append({"name": name, "guideline_pdf": pdf_url})

    return schemes


if __name__ == "__main__":
    schemes = fetch_scheme_list()
    print(f"Found {len(schemes)} schemes\n")
    for s in schemes:
        print(f" - {s['name']}")
        print(f"   {s['guideline_pdf']}\n")

    with open("scraped_scheme_links.json", "w") as f:
        json.dump(schemes, f, indent=2)
    print(f"\nSaved to scraped_scheme_links.json")