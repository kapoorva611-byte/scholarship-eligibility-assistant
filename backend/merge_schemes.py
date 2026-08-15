"""
Stage 3: merge reviewed scraped_schemes_extracted.json into the live
data/schemes.json. This is deliberately NOT automatic-on-extraction —
you should open scraped_schemes_extracted.json and eyeball it first,
since it came from an LLM reading messy PDFs and could contain mistakes.

Safe by design:
- Backs up schemes.json before writing, so a bad merge is always reversible.
- Skips any scheme_id that already exists (so re-running this after a
  second scrape/extract run later doesn't create duplicates).
- Validates that each incoming scheme has the minimum required fields
  before accepting it, so a malformed extraction can't silently corrupt
  the dataset the rule engine depends on.
"""
import json
import shutil
from pathlib import Path

SCHEMES_PATH = Path("data/schemes.json")
EXTRACTED_PATH = Path("scraped_schemes_extracted.json")
BACKUP_PATH = Path("data/schemes.json.bak")

REQUIRED_FIELDS = ["scheme_id", "name"]


def normalize(scheme: dict) -> dict:
    return {
        "scheme_id": scheme.get("scheme_id"),
        "name": scheme.get("name"),
        "ministry": scheme.get("ministry") or "Not specified",
        "category": scheme.get("category") or [],
        "education_level": scheme.get("education_level") or [],
        "income_limit_inr": scheme.get("income_limit_inr"),
        "gender": scheme.get("gender") or "any",
        "states": scheme.get("states") or ["ALL"],
        "benefit": scheme.get("benefit") or "Not specified — check official guidelines",
        "deadline": scheme.get("deadline") or "Check NSP for current dates",
        "apply_link": scheme.get("apply_link") or "https://scholarships.gov.in",
        "documents_required": scheme.get("documents_required") or [],
        "description": scheme.get("description") or "",
    }


def main():
    if not EXTRACTED_PATH.exists():
        print(f"No {EXTRACTED_PATH} found — run extractor.py first.")
        return

    with open(SCHEMES_PATH, "r") as f:
        existing = json.load(f)
    existing_ids = {s["scheme_id"] for s in existing}

    with open(EXTRACTED_PATH, "r") as f:
        candidates = json.load(f)

    added, skipped_duplicate, skipped_invalid = [], [], []

    for c in candidates:
        missing = [field for field in REQUIRED_FIELDS if not c.get(field)]
        if missing:
            skipped_invalid.append((c.get("name", "UNKNOWN"), missing))
            continue

        if c["scheme_id"] in existing_ids:
            skipped_duplicate.append(c["scheme_id"])
            continue

        existing.append(normalize(c))
        existing_ids.add(c["scheme_id"])
        added.append(c["scheme_id"])

    if added:
        shutil.copy(SCHEMES_PATH, BACKUP_PATH)
        with open(SCHEMES_PATH, "w") as f:
            json.dump(existing, f, indent=2)

    print(f"Added {len(added)} new scheme(s): {added}")
    print(f"Skipped {len(skipped_duplicate)} duplicate(s): {skipped_duplicate}")
    if skipped_invalid:
        print(f"Skipped {len(skipped_invalid)} invalid record(s):")
        for name, missing in skipped_invalid:
            print(f"   - '{name}' missing: {missing}")

    print(f"\nTotal schemes now in {SCHEMES_PATH}: {len(existing)}")
    if added:
        print(f"Backup of previous version saved to {BACKUP_PATH}")


if __name__ == "__main__":
    main()