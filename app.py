import streamlit as st
import sqlite3
import pandas as pd

st.set_page_config(page_title="News Dashboard", layout="wide")

st.title("📰 News Headlines Dashboard")

# Load from DB
conn = sqlite3.connect("data/news.db")
df = pd.read_sql("SELECT * FROM headlines ORDER BY scraped_at DESC", conn)

# Filters
search = st.text_input("🔍 Search headlines")
if search:
    df = df[df["headline"].str.contains(search, case=False)]

date_filter = st.date_input("📅 Filter by date")
if date_filter:
    df = df[df["scraped_at"].str.startswith(str(date_filter))]

st.write(f"Showing {len(df)} headlines")

# Display
st.dataframe(df)

# Download buttons
st.download_button("Download CSV", df.to_csv(index=False), "headlines.csv")
st.download_button("Download JSON", df.to_json(orient="records", indent=2), "headlines.json")
