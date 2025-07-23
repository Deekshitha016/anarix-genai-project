import os
from dotenv import load_dotenv
load_dotenv()

import time
import sqlite3
import pandas as pd
import matplotlib.pyplot as plt

from fastapi import FastAPI
from fastapi.responses import JSONResponse, StreamingResponse
from pydantic import BaseModel
import requests

# Set non-GUI backend for Matplotlib
plt.switch_backend("Agg")

app = FastAPI()

# Config
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
OPENROUTER_MODEL = "mistralai/mistral-7b-instruct"

# Pydantic Model
class QuestionRequest(BaseModel):
    question: str

# Call OpenRouter LLM
def get_sql_from_llm(question: str) -> str:
    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json"
    }

    prompt = f"""
You are a helpful assistant. Translate the following natural language question into a valid SQLite SQL query.
The database has the following tables:

1. total_sales_metrics (item_id, total_sales, total_units_ordered)
2. ad_sales_metrics (item_id, ad_sales, ad_spend, clicks)
3. eligibility_table (item_id, eligibility, message)

Only return the SQL. Do not explain anything.

Question: "{question}"
"""

    body = {
        "model": OPENROUTER_MODEL,
        "messages": [
            {"role": "user", "content": prompt}
        ]
    }

    response = requests.post("https://openrouter.ai/api/v1/chat/completions", json=body, headers=headers)

    if response.status_code != 200:
        raise Exception(f"OpenRouter API Error: {response.text}")

    llm_response = response.json()['choices'][0]['message']['content']
    sql = llm_response.strip().split('\n')[0]
    return sql.strip("`").strip("```sql").strip("```")

# Run SQL
def query_database(sql: str):
    try:
        conn = sqlite3.connect("ecommerce_data.db")
        cursor = conn.cursor()
        cursor.execute(sql)
        rows = cursor.fetchall()
        col_names = [desc[0] for desc in cursor.description]
        conn.close()
        return [dict(zip(col_names, row)) for row in rows]
    except Exception as e:
        return {"error": f"SQL Error: {str(e)}"}

# Chart generator
def generate_chart(data: list, title="Chart", x_label=None, y_label=None):
    if not data or not isinstance(data, list):
        return None
    try:
        keys = list(data[0].keys())
        x = [str(d[keys[0]]) for d in data]
        y = [d[keys[1]] for d in data]

        plt.figure(figsize=(10, 6))
        plt.bar(x, y, color="skyblue")
        plt.title(title)
        plt.xlabel(x_label or keys[0])
        plt.ylabel(y_label or keys[1])
        plt.xticks(rotation=45)
        plt.tight_layout()
        plt.savefig("chart.png")
        return "chart.png"
    except Exception as e:
        print("Chart error:", e)
        return None

# Ask endpoint
@app.post("/ask")
def ask(request: QuestionRequest):
    try:
        question_text = request.question.strip().lower()

        # Hardcoded fallback queries
        if question_text == "show total sales per item":
            sql_query = """
                SELECT item_id, SUM(total_sales) AS total_sales
                FROM total_sales_metrics
                GROUP BY item_id
            """
        elif question_text == "calculate the roas":
            sql_query = """
                SELECT 
                    a.item_id, 
                    ROUND(SUM(t.total_sales) / SUM(a.ad_spend), 2) AS roas
                FROM ad_sales_metrics a
                JOIN total_sales_metrics t ON a.item_id = t.item_id
                GROUP BY a.item_id
            """
        elif question_text == "which product had the highest cpc?":
            sql_query = """
                SELECT 
                    item_id, 
                    ROUND(ad_spend / clicks, 2) AS cpc
                FROM ad_sales_metrics
                WHERE clicks > 0
                ORDER BY cpc DESC
                LIMIT 1
            """
        else:
            sql_query = get_sql_from_llm(request.question)

        result = query_database(sql_query)

        chart = None
        if isinstance(result, list) and len(result) > 0 and "per" in question_text:
            chart = generate_chart(result)

        return {
            "question": request.question,
            "generated_sql": sql_query,
            "result": result,
            "chart": chart
        }

    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=500)

# Typing effect stream endpoint
@app.post("/ask-stream")
def ask_stream(request: QuestionRequest):
    def event_stream():
        try:
            question_text = request.question.strip().lower()
            yield f"You: {question_text}\n\n"
            time.sleep(0.5)

            # Same logic reused
            if question_text == "show total sales per item":
                sql_query = """
                    SELECT item_id, SUM(total_sales) AS total_sales
                    FROM total_sales_metrics
                    GROUP BY item_id
                """
            elif question_text == "calculate the roas":
                sql_query = """
                    SELECT 
                        a.item_id, 
                        ROUND(SUM(t.total_sales) / SUM(a.ad_spend), 2) AS roas
                    FROM ad_sales_metrics a
                    JOIN total_sales_metrics t ON a.item_id = t.item_id
                    GROUP BY a.item_id
                """
            elif question_text == "which product had the highest cpc?":
                sql_query = """
                    SELECT 
                        item_id, 
                        ROUND(ad_spend / clicks, 2) AS cpc
                    FROM ad_sales_metrics
                    WHERE clicks > 0
                    ORDER BY cpc DESC
                    LIMIT 1
                """
            else:
                sql_query = get_sql_from_llm(request.question)

            yield "Assistant is typing...\n\n"
            time.sleep(0.5)

            result = query_database(sql_query)

            if isinstance(result, list):
                result_text = "\n".join(str(r) for r in result)
            else:
                result_text = str(result)

            for char in f"Answer: {result_text}":
                yield char
                time.sleep(0.005)

            if isinstance(result, list) and len(result) > 0 and "per" in question_text:
                chart = generate_chart(result)
                if chart:
                    yield f"\n\n[Chart generated: {chart}]"

        except Exception as e:
            yield f"\n\n[Error] {str(e)}"

    return StreamingResponse(event_stream(), media_type="text/plain")
