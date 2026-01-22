import streamlit as st
from text_to_sql import text_to_sql_rag
from retrieval_pipeline import query_faiss, generate_response

st.set_page_config(page_title="RAG System", layout="centered")

# User input
question = st.text_input(
    "Enter your question",
    placeholder="Who is Daniel Killebrew?"
)

# Mode selection
mode = st.radio(
    "Choose retrieval method:",
    ["Text-to-SQL", "Vector RAG"]
)

if st.button("Get Answer") and question:
    with st.spinner("Processing..."):
        try:
            if mode == "Text-to-SQL":
                answer = text_to_sql_rag(question)

            else:
                chunks = query_faiss(question, k=100)
                answer = generate_response(chunks, question)

            st.success("Answer:")
            st.write(answer)

        except Exception as e:
            st.error(f"Error: {e}")
