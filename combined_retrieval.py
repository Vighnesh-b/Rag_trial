from LlmComm import askLlm
import json
from text_to_sql import text_to_sql_rag, multiple_questions_to_sql
from retrieval_pipeline import query_faiss,generate_response

original_question="Give me the average salary of men"
print("Original Question: ",original_question)
prompt = f"""
You are an expert data analyst assisting a hybrid SQL + RAG system.

Your task is to analyze the user's question using the schema provided.
DO NOT generate SQL or answers.

Schema:
employees(
    Employee_ID INTEGER,
    Name TEXT,
    Age INTEGER,
    Gender TEXT (Male or Female),
    Department TEXT,
    Job_Title TEXT,
    Experience_Years INTEGER,
    Education_Level TEXT,
    Location TEXT,
    Salary INTEGER
)

User question:
{original_question}

Instructions:

1. If the question is broad, vague, or exploratory, decompose it into at most 5 concrete subquestions.
2. If the question is already specific, return it as a single question.
3. For EACH question:
   - Label it as "text-to-sql" if it can be answered using ONLY the database schema above
   - Label it as "rag" ONLY if it requires external, semantic, or unstructured knowledge
4. Do NOT assume or invent values for any columns (e.g., job titles, locations).

Output ONLY valid JSON in the following format:

[{{
    "question": "...",
    "label": "text-to-sql" | "rag"
  ,...
  }}
]
"""

model= "tngtech/deepseek-r1t2-chimera:free"

print("\n========question splitting==========")
response = askLlm(prompt,model,800,0.2)
print(response)
print("======question splitting done==========\n")

try:
    response = json.loads(response)
except json.JSONDecodeError as e:
    raise RuntimeError("Invalid JSON from LLM") from e

t2s_questions=""
rag_summaries=[]
for i in range(len(response)):
    question=response[i]['question']
    label=response[i]['label']
    print("processing question ",i+1,f" {question},{label}...")
    if label=="text-to-sql":
        t2s_questions+=f"{i+1}. {question}"

    elif label=="rag":
        ans=generate_response(query_faiss(question,10),question)
        rag_summaries+={"question":question,"answer":ans}

t2s_summaries=multiple_questions_to_sql(t2s_questions)
rag_summaries=json.dumps(rag_summaries)
print("t2s:",t2s_summaries)
print("RAG:",rag_summaries)
summarization_prompt = f"""
You are a data analyst.

Using ONLY the information in the JSON below, write an insight-focused summary of the data that answers the users question given below.
Include key numbers (counts, averages, distributions) to support each insight.
You may interpret patterns and comparisons, but do not introduce facts not present in the data.

Write 1–3 concise paragraphs, grounded in the evidence.

user-question:
{original_question}
JSON:
{t2s_summaries}
{rag_summaries}
"""

print(askLlm(summarization_prompt,model,800,0.2))


