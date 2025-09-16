# ragapp/query_tester.py
from langchain_community.vectorstores import FAISS
from langchain.prompts import PromptTemplate
from langchain.chains import RetrievalQA
from langchain_huggingface import HuggingFaceEmbeddings
from core.llm_loader import load_llm

# Prompt
from langchain.prompts import PromptTemplate


# Load embeddings + FAISS index
embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
db = FAISS.load_local("schema_index", embeddings, allow_dangerous_deserialization=True)
retriever = db.as_retriever()

# Load LLM
llm = load_llm(model_type="groq", model_name="llama3-8b-8192")

prompt = PromptTemplate(
    input_variables=["context", "question"],
    template="""
You are an expert SQL assistant for a lottery system that generates **valid SQLite** queries only.
Please carefully review the question, especially terms like over, last, this, yesterday, etc.
Use the schema and context below carefully to produce exact SQL queries.

Schema & Context:
{context}

---

Guidelines:

1. SQL Query Requirements:
   - Use exact table and column names from the schema.
   - Join tables using the foreign keys described (User → Ticket → Bet).
   - Use aggregation functions like SUM, COUNT, AVG as needed.
   - Return valid SQLite SQL only; do not use unsupported features or syntax.

When asked for time ranges like "last 30 days":
- Always calculate relative to the current date/time.
- Use datetime functions, not just DATE().
- Ensure inclusivity: include today if required.
- Group results by full days, not timestamps.


2. Timezone & Date Handling ():
   - Ranges:
     - Today: datetime('now','localtime','start of day') → datetime('now','localtime','start of day','+1 day','-1 second')
     - Yesterday: datetime('now','localtime','-1 day','start of day') → datetime('now','localtime','-1 day','start of day','+1 day','-1 second')
     - This week: Monday 00:00 IST → now
     - Last week: Monday 00:00 IST (prev week) → Sunday 23:59:59 IST
     - This month: 1st of current month 00:00 IST → now
     - Last month: 1st of last month 00:00 IST → end of last month
     - Last 7/30 days: Rolling windows in IST.


3. Domain Specifics:
   - Users have multiple Tickets.
   - Tickets have multiple Bets.
   - Bets link to Users and Tickets.
   - Bets have `bet_amount`, `placed_at`, `status`.
   - Tickets have `draw_date`, `status`.
   - Users have `created_at`, `kyc_verified`, `is_active`, etc.

4. Output Formatting:
   - All numeric values must be rounded to 2 decimal places.
   - Use **`ROUND(value, 2)`** for numeric rounding.
   - If a fixed 2-decimal string format is required (e.g., 10 → 10.00), use **`printf('%.2f', value)`** in the SELECT clause.
   - Always alias aggregated/rounded values clearly (e.g., `AS total_bets`, `AS avg_amount`).

5. Final Answer:
   - Return only the SQL query string.
   - SQL must be inside this block:
```sql
SELECT ...
FROM ...

Generate the SQL query for this user question:

{question}
"""
)




# Build QA chain
qa_chain = RetrievalQA.from_chain_type(
    llm=llm,
    retriever=retriever,
    return_source_documents=True,
    chain_type_kwargs={"prompt": prompt}
)

def test_question(question: str):
    """Call this function to test schema Q&A without API"""
    result = qa_chain.invoke({"query": question})
    reply = result["result"].replace("\\n", " ").replace("\n", " ")

    return {
        "reply": reply,
        "sources": [doc.page_content for doc in result["source_documents"]]
    }


def call_llm(prompt: str) -> str:
    """
    Call the LLM directly with a plain prompt (no retrieval).
    Useful for tasks like visualization recommendations, 
    or chart generation.
    """
    response = llm.invoke(prompt)
    if hasattr(response, "content"):  # Chat model
        return response.content
    return str(response)