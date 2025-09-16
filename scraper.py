import requests
from bs4 import BeautifulSoup
import pandas as pd
import sqlite3
from datetime import datetime
import os

DB_PATH = "data/news.db"

# ---------------- DB FUNCTIONS ---------------- #
def init_db(db_path=DB_PATH):
    """Ensure the headlines table exists before inserting."""
    os.makedirs("data", exist_ok=True)
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
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

def save_to_db(df, db_path=DB_PATH):
    """Append scraped data into SQLite safely."""
    init_db(db_path)
    conn = sqlite3.connect(db_path)
    df.to_sql("headlines", conn, if_exists="append", index=False)
    conn.close()

# ---------------- SCRAPER FUNCTIONS ---------------- #
def scrape_bbc():
    """Scrape BBC News headlines."""
    url = "https://www.bbc.com/news"
    r = requests.get(url)
    soup = BeautifulSoup(r.text, "html.parser")
    headlines = [h.get_text(strip=True) for h in soup.find_all("h2") if len(h.get_text(strip=True).split()) > 3]

    return pd.DataFrame({
        "headline": headlines,
        "source": "BBC",
        "scraped_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    })

def scrape_cnn():
    """Scrape CNN News headlines."""
    url = "https://edition.cnn.com/world"
    r = requests.get(url)
    soup = BeautifulSoup(r.text, "html.parser")
    headlines = [h.get_text(strip=True) for h in soup.find_all("span", class_="container__headline-text") if h.get_text(strip=True)]

    return pd.DataFrame({
        "headline": headlines,
        "source": "CNN",
        "scraped_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    })

def scrape_ht():
    """Scrape Hindustan Times headlines."""
    url = "https://www.hindustantimes.com/latest-news"
    r = requests.get(url)
    soup = BeautifulSoup(r.text, "html.parser")
    headlines = [h.get_text(strip=True) for h in soup.find_all("h3") if h.get_text(strip=True)]

    return pd.DataFrame({
        "headline": headlines,
        "source": "Hindustan Times",
        "scraped_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    })

# ---------------- MAIN PIPELINE ---------------- #
def run_scraper():
    os.makedirs("data", exist_ok=True)

    # Collect from multiple sources
    all_dfs = []
    try:
        all_dfs.append(scrape_bbc())
        print("✅ BBC scraped")
    except Exception as e:
        print("❌ BBC failed:", e)

    try:
        all_dfs.append(scrape_cnn())
        print("✅ CNN scraped")
    except Exception as e:
        print("❌ CNN failed:", e)

    try:
        all_dfs.append(scrape_ht())
        print("✅ Hindustan Times scraped")
    except Exception as e:
        print("❌ HT failed:", e)

    # Merge everything into one dataframe
    if all_dfs:
        df = pd.concat(all_dfs, ignore_index=True)

        # Save to CSV (append mode)
        df.to_csv(
            "data/headlines.csv",
            index=False,
            mode="a",
            header=not os.path.exists("data/headlines.csv")
        )

        # Save latest scrape batch to JSON
        df.to_json("data/headlines.json", orient="records", indent=2)

        # Save to SQLite
        save_to_db(df)

        print(f"🚀 Total {len(df)} headlines saved to CSV, JSON, and DB.")
    else:
        print("⚠️ No headlines scraped.")

if __name__ == "__main__":
    run_scraper()
