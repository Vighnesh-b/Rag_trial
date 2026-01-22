import sqlite3
from LlmComm import askLlm

def generate_sql(question):
    prompt = f"""
    You are an expert SQL assistant.

    Schema:
    employees(
    Employee_ID INTEGER,
    Name TEXT,
    Age INTEGER,
    Gender TEXT,
    Department TEXT,
    Job_Title TEXT,
    Experience_Years INTEGER,
    Education_Level TEXT,
    Location TEXT,
    Salary INTEGER
    )

    Rules:
    - Output ONLY valid SQLite SQL
    - Use exact column names
    - Do NOT include explanations
    - Do NOT use markdown

    Question:
    {question}
    """
    model= "meta-llama/llama-3.3-70b-instruct:free"
    response = askLlm(prompt,model)
    return response

def run_sql(sql):
    conn = sqlite3.connect("employeeDB.db")
    cursor = conn.cursor()

    cursor.execute(sql)
    rows = cursor.fetchall()
    columns = [desc[0] for desc in cursor.description]
    conn.close()
    return columns, rows

def format_answer(question, columns, rows):
    if not rows:
        return "Information not found in the database."

    context = "\n".join(
        ", ".join(f"{col}: {val}" for col, val in zip(columns, row))
        for row in rows
    )

    prompt = f"""
Use the following database results to answer the question.
Provide the answer in a small paragraphs.
Do not add extra information.

Question:
{question}

Results:
{context}
"""
    model="xiaomi/mimo-v2-flash:free"
    response = askLlm(prompt,model,800,0.2)

    return response

def text_to_sql_rag(question):
    print(question)
    sql = generate_sql(question)
    print("Generated SQL:", sql)

    columns, rows = run_sql(sql)
    return format_answer(question, columns, rows)

if __name__ == "__main__":
    q = "Who is Daniel Killebrew?"
    print(text_to_sql_rag(q))


