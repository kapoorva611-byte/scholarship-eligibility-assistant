from sentence_transformers import SentenceTransformer, util

print("Loading embedding model (first run downloads it, ~80MB, one-time)...")
model = SentenceTransformer("all-MiniLM-L6-v2")
print("Model loaded.\n")

sentences = [
    "What is the income limit for OBC scholarship eligibility?",
    "How much can my family earn to qualify as OBC?",
    "What is the best biryani recipe?",
]

embeddings = model.encode(sentences)

print("Shape of one embedding:", embeddings[0].shape)
print("First 8 numbers of sentence 1's embedding:", embeddings[0][:8])
print()

sim_1_2 = util.cos_sim(embeddings[0], embeddings[1]).item()
sim_1_3 = util.cos_sim(embeddings[0], embeddings[2]).item()

print(f"Similarity between sentence 1 and 2 (both about OBC income): {sim_1_2:.4f}")
print(f"Similarity between sentence 1 and 3 (OBC vs biryani):        {sim_1_3:.4f}")