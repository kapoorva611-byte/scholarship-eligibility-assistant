import os
import time
from dotenv import load_dotenv
from google import genai
from google.genai import types

load_dotenv()
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

SYSTEM_INSTRUCTION = """You are a scholarship assistant. You answer ONLY using \
the provided source excerpts about scholarship schemes.

Rules:
- If the excerpts don't contain enough information, say so plainly instead of guessing.
- When you use a fact, cite it like this: (Source 1).
- Be clear and encouraging, not robotic.
"""


def _build_prompt(question: str, chunks: list[dict]) -> str:
    blocks = []
    for i, c in enumerate(chunks, start=1):
        blocks.append(f"[Source {i} — {c['scheme_name']}]\n{c['text']}")
    context = "\n\n".join(blocks)
    return f"""Source excerpts:

{context}

Question: {question}

Answer using only the excerpts above. Cite sources like (Source 1) inline."""


def generate_answer(question: str, chunks: list[dict], max_retries: int = 3) -> str:
    if not chunks:
        return "I couldn't find relevant information to answer that."

    prompt = _build_prompt(question, chunks)
    config = types.GenerateContentConfig(system_instruction=SYSTEM_INSTRUCTION)

    last_error = None
    for attempt in range(max_retries):
        try:
            response = client.models.generate_content(
                model="gemini-flash-latest",
                contents=prompt,
                config=config,
            )
            return response.text
        except Exception as e:
            last_error = e
            wait = 2 ** attempt  # 1s, 2s, 4s
            print(f"[llm] Attempt {attempt + 1} failed ({e}), retrying in {wait}s...")
            time.sleep(wait)

    return f"Sorry, the AI service is temporarily unavailable after {max_retries} attempts. Please try again shortly. (Last error: {last_error})"