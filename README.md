# Scholarship Eligibility Assistant (In Progress)

A hybrid rule-based + RAG system that matches Indian students to real
government scholarship schemes based on income, category, education
level, gender, and state — then answers follow-up questions grounded in
official scheme documents.

## Status
- ✅ Deterministic eligibility engine (Python) — filters students against
  structured scheme data across 5 criteria
- ✅ REST API with FastAPI + Pydantic validation
- 🚧 RAG pipeline (ChromaDB, sentence-transformers, Gemini API) for
  grounded natural-language Q&A with citations — in progress

## Stack
Python, FastAPI, Pydantic, ChromaDB (upcoming), Gemini API (upcoming)

## Run locally
\`\`\`
cd backend
python -m venv venv
venv\Scripts\activate
python -m pip install fastapi "uvicorn[standard]" python-dotenv pydantic
python -m uvicorn main:app --reload --port 8000
\`\`\`
Then visit `http://127.0.0.1:8000/docs` to try the eligibility endpoint.
