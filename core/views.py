# backend/views.py
import json,re
from django.shortcuts import render
from core.process import process
from core.utils.profiling import profile_records
from core.utils.prompts import build_viz_prompt
from core.query_generator import call_llm
import random

def clean_llm_json(text: str) -> str:
    # remove markdown fences if present
    text = re.sub(r"```.*?```", lambda m: m.group(0).strip("`"), text, flags=re.S)
    text = text.replace("```json", "").replace("```", "").strip()
    return text

import re, json

def extract_json(text: str):
    """
    Extract the first JSON object found in the text.
    """
    try:
        match = re.search(r"\{.*\}", text, re.S)  # find first {...}
        if match:
            return json.loads(match.group(0))
    except Exception as e:
        print("JSON extraction failed:", e)
    return None


def dashboard_view(request):
    query = reply = None
    output = []
    viz_spec = None
    error = None

    if request.method == "POST":
        try:
            question = request.POST.get("question", "").strip()
            if question:
                data = process(question)                 # your NL→SQL→rows pipeline
                query = data.get("sql")
                reply = data.get("raw_reply")
                rows  = data.get("results", [])
                error = data.get("error")
                if error:
                    funny_messages = [
                        "Whoa there, cowboy! I only read data, not break it. No UPDATE/DELETE shenanigans here.",
                        "Nice try! But if I start modifying data, the DBA union will revoke my membership.",
                        "Sorry, I’m strictly a SELECT-ive listener. Updates and deletes give me trust issues.",
                        "Error 404: Permission to destroy databases not found. Please contact… nobody.",
                        "I asked my lawyer, and they said I’m not allowed to UPDATE or DELETE. SELECT only, please.",
                        "Oops! I’m on a strict data diet. No CREATE/UPDATE/DELETE calories allowed.",
                        "I’d love to help… but last time I updated data, I accidentally deleted the internet.",
                        "Danger detected! Your request has been sent to the Ministry of Bad Ideas.",
                        "I could run that query… or we could both stay employed. SELECT wisely.",
                        "Think of me as read-only mode with a sense of humor. Your data is safe from me.",
                    ]
                    error = random.choice(funny_messages)
                if isinstance(rows, str):
                    try: rows = json.loads(rows)
                    except: rows = []
                output = rows if isinstance(rows, list) else []

                # ask LLM for a visualization spec
                profile = profile_records(output)
                five_records = profile['samples'][:5]
                if profile["row_count"] > 0:
                    prompt = build_viz_prompt(five_records, question=question, sql=query)
                    viz_text = call_llm(prompt)  # <- implement
                    cleaned = clean_llm_json(viz_text)
                    viz_spec = extract_json(viz_text)
                    print(viz_spec,"0000000000000000000000000000000")
                    if not isinstance(viz_spec, dict): viz_spec = None
        except Exception as e:
            error = str(e)
    return render(request, "dashboard.html", {
    "query": query,
    "reply": reply,
    "output": output,   # normal Python list/dict for Django loops
    "output_json": json.dumps(output, default=str),  # safe JSON string for JS
    "viz_spec": json.dumps(viz_spec, default=str),
    "error": error,
})

