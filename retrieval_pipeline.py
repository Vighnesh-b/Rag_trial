import sqlite3
import numpy as np
import faiss
from sentence_transformers import SentenceTransformer
from LlmComm import askLlm

DB_PATH = "employeeDB.db"
FAISS_INDEX_PATH = "employees.index"
ROWS_PER_CHUNK = 1

def query_faiss(question, k=5):
    model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")

    query_embedding = model.encode(
        [question],
        normalize_embeddings=True
    ).astype("float32")

    index = faiss.read_index(FAISS_INDEX_PATH)
    D, I = index.search(query_embedding, k)

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    results = []
    for idx in I[0]:
        cursor.execute(
            "SELECT text FROM chunks WHERE chunk_id = ?",
            (int(idx),)
        )
        row = cursor.fetchone()
        if row:
            results.append(row[0])

    conn.close()
    return results

def generate_response(chunks, query):

    model="xiaomi/mimo-v2-flash:free"
    context = "\n".join(chunks)
    prompt = f"""
    You are an assistant summarizing employee records.

    Use ONLY the information provided in the context below.
    Do NOT add assumptions, external knowledge.

    Context:
    {context}

    Task:
    Answer the question: "{query}"

    Be concise and summarize the Information given such that it answers the question.

    If no relevant information is found, output exactly:
    Information not found in the provided data.
    """
    response=askLlm(prompt, model, 800, 0.2)
    return response

if __name__=="__main__":

    question="Who is Daniel Killebrew?"
    chunks=query_faiss(question,50)
    print("\n".join(chunks))
    print(generate_response(chunks,question))
