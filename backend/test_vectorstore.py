from services.eligibility import SCHEMES
from services.vectorstore import ingest_all_schemes, query_chunks
from services.llm import generate_answer

ingest_all_schemes(SCHEMES)

question = "I am a girl in class 12, is there any scholarship for me?"
shortlist = ["cbse-single-girl-child", "css-college"]

chunks = query_chunks(question, scheme_ids=shortlist, top_k=3)
answer = generate_answer(question, chunks)

print("Question:", question)
print("\nAnswer:\n", answer)