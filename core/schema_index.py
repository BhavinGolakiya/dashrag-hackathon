# rag/schema_index.py
from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings

schema_docs = [
    # User table
    """
    Table: User
    Columns:
      - id (Primary Key, AutoField)
      - user_code (CharField, unique)
      - username (CharField, unique)
      - email (EmailField, unique)
      - first_name (CharField, nullable)
      - last_name (CharField, nullable)
      - role (CharField, choices: player, admin, default=player)
      - is_active (BooleanField, default=True)
      - kyc_verified (BooleanField, default=False)
      - sign_in_ip (GenericIPAddressField, nullable)
      - last_login (DateTimeField, auto_now)
      - created_at (DateTimeField, auto_now_add)
      - updated_at (DateTimeField, auto_now)
    """,

    # Ticket table
    """
    Table: Ticket
    Columns:
      - id (Primary Key, AutoField)
      - user_id (ForeignKey -> User.id)
      - ticket_number (CharField)
      - game_name (CharField)
      - price (DecimalField, max_digits=10, decimal_places=2)
      - status (CharField, choices: active, cancelled, expired, default=active)
      - purchased_at (DateTimeField, auto_now_add)
      - draw_date (DateTimeField)
      - created_at (DateTimeField, auto_now_add)
      - updated_at (DateTimeField, auto_now)
    """,

    # Bet table
    """
    Table: Bet
    Columns:
      - id (Primary Key, AutoField)
      - user_id (ForeignKey -> User.id)
      - ticket_id (ForeignKey -> Ticket.id)
      - bet_amount (DecimalField, max_digits=10, decimal_places=2)
      - potential_win (DecimalField, nullable, blank=True)
      - status (CharField, choices: pending, won, lost, default=pending)
      - placed_at (DateTimeField, auto_now_add)
      - resolved_at (DateTimeField, nullable)
      - created_at (DateTimeField, auto_now_add)
      - updated_at (DateTimeField, auto_now)
    """,

    # Relationships
    "Relation: User 1---N Ticket (a user can have many tickets)",
    "Relation: User 1---N Bet (a user can have many bets)",
    "Relation: Ticket 1---N Bet (a ticket can have many bets)"

]

def build_schema_index():
    embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
    vectorstore = FAISS.from_texts(schema_docs, embeddings)
    vectorstore.save_local("schema_index")
    return vectorstore
