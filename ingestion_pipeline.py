import sqlite3
import numpy as np
import faiss
from sentence_transformers import SentenceTransformer

DB_PATH = "employeeDB.db"
FAISS_INDEX_PATH = "employees.index"
ROWS_PER_CHUNK = 1

def row_to_text(row):
    return (
        f"Employee Record | "
        f"ID: {row['Employee_ID']} | "
        f"Name: {row['Name']} | "
        f"Age: {row['Age']} | "
        f"Gender: {row['Gender']} | "
        f"Department: {row['Department']} | "
        f"Role: {row['Job_Title']} | "
        f"Experience: {row['Experience_Years']} years | "
        f"Education: {row['Education_Level']} | "
        f"Location: {row['Location']} | "
        f"Salary: {row['Salary']}"
    )

def create_chunks(db_path, rows_per_chunk):
    chunks = []
    buffer = []

    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM employees ORDER BY Employee_ID")

    for row in cursor:
        buffer.append(row_to_text(row))

        if len(buffer) >= rows_per_chunk:
            chunks.append(" ".join(buffer))
            buffer = []

    if buffer:
        chunks.append(" ".join(buffer))

    conn.close()
    return chunks

def store_chunks(chunks, db_path):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS chunks (
            chunk_id INTEGER PRIMARY KEY,
            text TEXT
        )
    """)

    cursor.execute("DELETE FROM chunks")

    cursor.executemany(
        "INSERT INTO chunks (chunk_id, text) VALUES (?, ?)",
        [(i, chunk) for i, chunk in enumerate(chunks)]
    )

    conn.commit()
    conn.close()

def build_faiss_index(chunks):
    model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")

    embeddings = model.encode(
        chunks,
        batch_size=32,
        show_progress_bar=True,
        normalize_embeddings=True
    ).astype("float32")

    dim = embeddings.shape[1]

    index = faiss.IndexIDMap(faiss.IndexFlatIP(dim))
    ids = np.arange(len(embeddings))

    index.add_with_ids(embeddings, ids)
    faiss.write_index(index, FAISS_INDEX_PATH)

    print(f"FAISS index built with {index.ntotal} vectors")

if __name__ == "__main__":
    chunks = create_chunks(DB_PATH, ROWS_PER_CHUNK)
    store_chunks(chunks, DB_PATH)
    build_faiss_index(chunks)

