from fastapi import FastAPI
from pydantic import BaseModel
from services.eligibility import check_eligibility, SCHEMES
from services.vectorstore import ingest_all_schemes, query_chunks
from fastapi.middleware.cors import CORSMiddleware
from services.llm import generate_answer

app = FastAPI(title="Scholarship Eligibility Assistant")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)
@app.on_event("startup")
def startup_ingest():
    count = ingest_all_schemes(SCHEMES)
    print(f"[startup] Ingested {count} schemes into vector store.")


class ProfileRequest(BaseModel):
    category: str | None = None
    education_level: str | None = None
    annual_family_income: float | None = None
    gender: str | None = None
    state: str | None = None


class QueryRequest(BaseModel):
    question: str
    scheme_ids: list[str] | None = None
    top_k: int = 3


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/eligibility/check")
def eligibility_check(profile: ProfileRequest):
    matches = check_eligibility(profile.model_dump(exclude_none=True))
    return {"matched_count": len(matches), "matches": matches}


@app.post("/query")
def query(req: QueryRequest):
    chunks = query_chunks(req.question, scheme_ids=req.scheme_ids, top_k=req.top_k)
    answer = generate_answer(req.question, chunks)
    sources = [{"scheme_id": c["scheme_id"], "scheme_name": c["scheme_name"], "score": c["score"]} for c in chunks]
    return {"answer": answer, "sources": sources}