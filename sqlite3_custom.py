import sqlite3

def init_db(db_path="data/news.db"):
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    
    # ✅ Create table if it does not exist
    cur.execute("""
        CREATE TABLE IF NOT EXISTS headlines (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            headline TEXT NOT NULL,
            source TEXT,
            scraped_at TEXT
        )
    """)
    
    conn.commit()
    conn.close()
