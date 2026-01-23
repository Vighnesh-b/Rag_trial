import sqlite3
from LlmComm import askLlm
import json
import re

def extract_json(text):
    match = re.search(r"\[.*?\]", text, re.DOTALL)
    if not match:
        raise ValueError("No JSON found")
    json_str = match.group()
    return json.loads(json_str)


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
    if not sql.strip().lower().startswith("select"):
        raise ValueError("Only SELECT queries are allowed")

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
    sql = generate_sql(question)

    columns, rows = run_sql(sql)
    return format_answer(question, columns, rows)

def multiple_questions_to_sql(questions):
    prompt = f"""
    You are an expert SQL assistant. You are working with a SQLite db and the schema of the table is given below.

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
    - Output ONLY in the JSON Answer format given below
    - Use correct syntax for SQLite database 
    - Use exact column names
    - Do NOT include explanations
    - Do NOT have '''sql or json or ''' markdowns 

    Question:
    {questions}

    Answer format:
    [
    {{
    "question" : ...,
    "sql-query" : ...
    }}, ...
    ]

    """

    model="meta-llama/llama-3.3-70b-instruct:free"
    sql_query_response=askLlm(prompt,model,800,0.2)
    sql_query_response=extract_json(sql_query_response)

    for i in range(len(sql_query_response)):
        sql=sql_query_response[i]['sql-query']
        cols,rows=run_sql(sql)
        sql_query_response[i]['database-result'] = "\n".join(
        ", ".join(f"{c}: {v}" for c, v in zip(cols, rows)))
    
    summarization_prompt=f"""
    Use the following database results to answer the question.
    Provide the answer in a small paragraphs.
    Do not add extra information.

    results: {json.dumps(sql_query_response, indent=2)}

    Answer format:
    [{{
    "question" : ...,
    "answer" : (this is the answer you get after analysing the question and database-result).... 
    }}]

    """

    summary_response=askLlm(summarization_prompt,"xiaomi/mimo-v2-flash:free",800,0.2)
    return summary_response

if __name__ == "__main__":
    # q = "Who is Daniel Killebrew?"
    # print(text_to_sql_rag(q))


    questions="""1. What is the gender distribution (count of employees by gender) in the HR department?,
    2. What is the average salary for each gender in the HR department?,
    3. What is the average experience years for each gender in the HR department?,
    4. How are education levels distributed among genders in the HR department?,
    5. How are job titles distributed among genders in the HR department?"""
    print(multiple_questions_to_sql(questions))



