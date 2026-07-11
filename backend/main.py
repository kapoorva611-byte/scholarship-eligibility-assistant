from fastapi import FastAPI
from pydantic import BaseModel
from services.eligibility import check_eligibility

app = FastAPI(title="Scholarship Eligibility Assistant")


class ProfileRequest(BaseModel):
    category: str | None = None
    education_level: str | None = None
    annual_family_income: float | None = None
    gender: str | None = None
    state: str | None = None


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/eligibility/check")
def eligibility_check(profile: ProfileRequest):
    matches = check_eligibility(profile.model_dump(exclude_none=True))
    return {"matched_count": len(matches), "matches": matches}