import json
import os

_DATA_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "schemes.json")

with open(_DATA_PATH, "r") as f:
    SCHEMES = json.load(f)
def _matches_category(scheme: dict, category: str) -> bool:
    if category is None:
        return True
    return category in scheme.get("category", [])
def _matches_income(scheme: dict, income: float) -> bool:
    cap = scheme.get("income_limit_inr")
    if cap is None or income is None:
        return True
    return income <= cap
def _matches_gender(scheme: dict, gender: str) -> bool:
    scheme_gender = scheme.get("gender", "any")
    if scheme_gender == "any" or gender is None:
        return True
    return scheme_gender == gender
def _matches_education_level(scheme: dict, level: str) -> bool:
    if level is None:
        return True
    return level in scheme.get("education_level", [])
def _matches_state(scheme: dict, state: str) -> bool:
    states = scheme.get("states", ["ALL"])
    if "ALL" in states or state is None:
        return True
    return state in states
def check_eligibility(profile: dict) -> list[dict]:
    category = profile.get("category")
    education_level = profile.get("education_level")
    income = profile.get("annual_family_income")
    gender = profile.get("gender")
    state = profile.get("state")

    matches = []
    for scheme in SCHEMES:
        if not _matches_category(scheme, category):
            continue
        if not _matches_education_level(scheme, education_level):
            continue
        if not _matches_income(scheme, income):
            continue
        if not _matches_gender(scheme, gender):
            continue
        if not _matches_state(scheme, state):
            continue

        matches.append(scheme)

    return matches