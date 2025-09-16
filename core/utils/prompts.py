# utils/prompts.py

import json
SPEC_CONTRACT = """
You are a visualization planner. Decide the most appropriate chart for the given tabular result.
Return ONLY a JSON object with this schema:
{chart, x:{field,type,time_unit}, y:{field,agg,type}, series_by, top_n, sort, reason, confidence}.
chart ∈ [line, bar, stacked_bar, pie, scatter, histogram, kpi].

Rules:
- If there is time (datetime) + numeric → line (x=time, y=metric, agg=sum).
- If one categorical + numeric → bar (top 20 by value).
- If two numeric → scatter.
- If single numeric → histogram (or kpi if small row_count).
- If low-cardinality categorical only → pie (<=10 slices).
- If nothing numeric/datetime → fallback to pie or kpi (count-based).
- Do not invent columns; only use existing ones.
- Use time_unit=auto unless obvious (month/year).
- series_by only if a second low-cardinality categorical exists (≤10 unique).
- Always pick some chart; never return "table_only" or "none".
- Always include a short 'reason' and 'confidence' 0..1.
"""

def build_viz_prompt(data_profile, question=None, sql=None):
    base = SPEC_CONTRACT
    context = {"data_profile": data_profile}
    if question:
        context["user_question"] = question
    if sql:
        context["sql_query"] = sql
    return f"""{base}

DATA PROFILE:
{json.dumps(data_profile, default=str)}
"""
