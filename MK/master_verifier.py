import fitz
import re
import numpy as np
from sentence_transformers import SentenceTransformer
from config import *

model = SentenceTransformer(EMBEDDING_MODEL)

CLAIM_KEYWORDS = [
    "causes", "results in", "leads to",
    "associated with", "correlated",
    "significant", "analysis shows",
    "study shows", "predicts"
]

def extract_pdf_pages(files):
    pages = []
    for f in files:
        doc = fitz.open(stream=f.read(), filetype="pdf")
        for i, page in enumerate(doc):
            text = page.get_text().strip()
            if text:
                pages.append({
                    "pdf": f.name,
                    "page": i + 1,
                    "text": text
                })
    return pages

def chunk_pages(pages):
    chunks = []
    for p in pages:
        words = p["text"].split()
        for i in range(0, len(words), CHUNK_SIZE - CHUNK_OVERLAP):
            chunk = " ".join(words[i:i+CHUNK_SIZE])
            if len(chunk.split()) > 20:
                chunks.append({**p, "chunk": chunk})
    return chunks

def embed(texts):
    return model.encode(texts, normalize_embeddings=True)

def similarity(a, b):
    return float(np.dot(a, b))

def extract_claims(chunks):
    claims = []
    for c in chunks:
        for s in re.split(r'(?<=[.!?])\s+', c["chunk"]):
            sl = s.lower()
            if any(k in sl for k in CLAIM_KEYWORDS):
                if 10 < len(s.split()) < 40:
                    claims.append(s.strip())
            if len(claims) >= CLAIM_LIMIT:
                return claims
    return claims

def verify_claims(claims, chunks):
    if not claims:
        return []

    claim_embs = embed(claims)
    chunk_embs = embed([c["chunk"] for c in chunks])

    results = []
    for i, claim in enumerate(claims):
        matches = []
        for j, c in enumerate(chunks):
            score = similarity(claim_embs[i], chunk_embs[j])
            if score >= SIMILARITY_THRESHOLD:
                matches.append({
                    "pdf": c["pdf"],
                    "page": c["page"],
                    "score": round(score, 3),
                    "text": c["chunk"]
                })
        results.append({
            "claim": claim,
            "verified": bool(matches),
            "matches": matches
        })
    return results

def answer_question(question, chunks, top_k=5):
    q_emb = embed([question])[0]
    c_embs = embed([c["chunk"] for c in chunks])

    scored = [(c, similarity(q_emb, e)) for c, e in zip(chunks, c_embs)]
    scored.sort(key=lambda x: x[1], reverse=True)

    if not scored or scored[0][1] < 0.35:
        return None, []

    return scored[0][0]["chunk"], scored[:top_k]

def run_pipeline(files):
    pages = extract_pdf_pages(files)
    chunks = chunk_pages(pages)
    claims = extract_claims(chunks)
    verification = verify_claims(claims, chunks)
    return pages, chunks, claims, verification
