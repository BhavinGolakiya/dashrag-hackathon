# core/process.py

import re
from django.apps import apps
from django.db import connection
from core.query_generator import test_question


def execute_sql(sql_query: str):
    """
    Execute a raw SQL query and return results as a list of dicts.
    """
    results = []
    with connection.cursor() as cursor:
        try:
            cursor.execute(sql_query)
            if cursor.description:
                columns = [col[0] for col in cursor.description]
                rows = cursor.fetchall()
                results = [dict(zip(columns, row)) for row in rows]
            else:
                results = {"rows_affected": cursor.rowcount}
        except Exception as e:
            return {"error": str(e)}
    return results


def replace_model_names_with_db_tables(sql_query: str, app_label="core"):
    """
    Replace Django model class names with actual DB table names in the SQL query.
    """
    models = apps.get_app_config(app_label).get_models()
    mapping = {model.__name__: model._meta.db_table for model in models}

    for model_name, table_name in mapping.items():
        sql_query = re.sub(rf"\b{model_name}\b", table_name, sql_query)

    return sql_query


import re

def extract_sql(reply: dict) -> str:
    """
    Extracts SQL query from a reply dict returned by LLM.
    """
    text = reply.get("reply", "")

    # ```sql ... ```
    match = re.search(r"```sql\s*(.*?)\s*```", text, re.DOTALL | re.IGNORECASE)
    if match:
        return match.group(1).strip()

    # fallback: look for SELECT ... ;
    match = re.search(r"\b(SELECT|INSERT|UPDATE|DELETE|CREATE|DROP|ALTER)[\s\S]+?;", text, re.IGNORECASE)
    if match:
        return match.group(0).strip()  # use group(0) to get the whole SQL query

    return ""




import re

def process(question: str):
    """
    Main pipeline:
    1. Generate SQL from question
    2. Extract SQL
    3. Replace model names with DB table names
    4. Execute SQL (only SELECT allowed)
    5. Return results
    """
    # Step 1: Get raw LLM output
    reply = test_question(question)

    # Step 2: Extract SQL from reply
    sql = extract_sql(reply)
    if not sql:
        return {"error": "Could not extract SQL from LLM reply", "raw_reply": reply}

    # Step 3: Replace Django model names with actual DB tables
    corrected_sql = replace_model_names_with_db_tables(sql)

    # Step 4: Allow only SELECT queries
    cleaned_sql = corrected_sql.strip().lower()
    if not cleaned_sql.startswith("select"):
        return {
            "error": "Only SELECT queries are allowed for security reasons.",
            "sql": corrected_sql,
            "raw_reply": reply,
        }

    try:
        # Step 5: Execute SQL
        results = execute_sql(corrected_sql)
    except Exception as e:
        return {"error": str(e), "sql": corrected_sql, "raw_reply": reply}

    return {
        "question": question,
        "raw_reply": reply,
        "sql": corrected_sql,
        "results": results,
    }
