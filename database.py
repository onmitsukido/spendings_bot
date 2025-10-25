import os
import psycopg2
from psycopg2.extras import RealDictCursor
from dotenv import load_dotenv

load_dotenv()

def get_db_connection():
    return psycopg2.connect(
        dbname=os.getenv("DB_NAME"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        host=os.getenv("DB_HOST"),
        port=os.getenv("DB_PORT"),
        cursor_factory=RealDictCursor
    )

def init_db():
    conn = get_db_connection()
    with conn.cursor() as cur:
        cur.execute("""
            CREATE TABLE IF NOT EXISTS transactions (
                id SERIAL PRIMARY KEY,
                user_id BIGINT NOT NULL,
                amount DECIMAL(12, 2) NOT NULL,
                category VARCHAR(100),
                type VARCHAR(10) CHECK (type IN ('income', 'expense')),
                created_at TIMESTAMP DEFAULT NOW()
            )
        """)
        conn.commit()
    conn.close()

def add_transaction(user_id: int, amount: float, category: str, trans_type: str):
    conn = get_db_connection()
    with conn.cursor() as cur:
        cur.execute(
            "INSERT INTO transactions (user_id, amount, category, type) VALUES (%s, %s, %s, %s)",
            (user_id, amount, category, trans_type)
        )
        conn.commit()
    conn.close()

def get_balance(user_id: int):
    conn = get_db_connection()
    with conn.cursor() as cur:
        cur.execute("""
            SELECT 
                COALESCE(SUM(CASE WHEN type = 'income' THEN amount ELSE 0 END), 0) AS income,
                COALESCE(SUM(CASE WHEN type = 'expense' THEN amount ELSE 0 END), 0) AS expense
            FROM transactions
            WHERE user_id = %s
        """, (user_id,))
        row = cur.fetchone()
    conn.close()
    return row["income"], row["expense"]