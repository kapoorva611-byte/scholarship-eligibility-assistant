import chromadb
from chromadb.utils import embedding_functions

client = chromadb.PersistentClient(path="./chroma_data")

embedding_fn = embedding_functions.SentenceTransformerEmbeddingFunction(
    model_name="all-MiniLM-L6-v2"
)

collection = client.get_or_create_collection(
    name="scholarship_schemes",
    embedding_function=embedding_fn,
)


def ingest_all_schemes(schemes: list[dict]):
    """Re-adds every scheme's retrieval-friendly text. Safe to call
    repeatedly — upsert overwrites existing ids instead of duplicating."""
    ids, documents, metadatas = [], [], []
    for scheme in schemes:
        gender_text = "for girls / female students only" if scheme.get("gender") == "female" else "open to all genders"
        levels_text = ", ".join(scheme.get("education_level", []))
        documents_text = ", ".join(scheme.get("documents_required", []))
        retrieval_text = (
            f"{scheme['name']}. "
            f"Eligible education levels: {levels_text}. "
            f"Gender: {gender_text}. "
            f"{scheme['description']} "
            f"Required documents: {documents_text}. "
            f"Application deadline: {scheme.get('deadline', 'not specified')}. "
            f"Apply at: {scheme.get('apply_link', 'not specified')}."
        )
        ids.append(scheme["scheme_id"])
        documents.append(retrieval_text)
        metadatas.append({"scheme_id": scheme["scheme_id"], "scheme_name": scheme["name"]})

    if ids:
        collection.upsert(ids=ids, documents=documents, metadatas=metadatas)
    return len(ids)


def query_chunks(question: str, scheme_ids: list[str] | None = None, top_k: int = 3) -> list[dict]:
    """
    If scheme_ids is given, ONLY searches within those schemes — this is
    what makes retrieval reliable in practice: we restrict the search
    space to schemes the rule engine already confirmed the student
    qualifies for, instead of searching all schemes blind.
    """
    if collection.count() == 0:
        return []

    where = {"scheme_id": {"$in": scheme_ids}} if scheme_ids else None

    results = collection.query(
        query_texts=[question],
        n_results=min(top_k, collection.count()),
        where=where,
    )

    out = []
    for doc, meta, dist in zip(results["documents"][0], results["metadatas"][0], results["distances"][0]):
        out.append({
            "text": doc,
            "scheme_id": meta["scheme_id"],
            "scheme_name": meta["scheme_name"],
            "score": round(1 - dist, 4),
        })
    return out