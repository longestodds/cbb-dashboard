import streamlit as st
import pandas as pd

st.set_page_config(page_title="CBB Betting Dashboard", page_icon="🏀", layout="centered")

st.markdown("""
    <style>
    .stApp { background-color: #090d16; color: #f3f4f6; }
    .card { background-color: #111827; border: 1px solid #1f2937; padding: 16px; border-radius: 12px; margin-bottom: 12px; }
    </style>
""", unsafe_allow_html=True)

st.title("🏀 CBB Betting Dashboard")
st.caption("Automated daily model projections & betting edges")

@st.cache_data(ttl=10)
def load_data():
    try:
        df = pd.read_json("data.json")
        return df
    except Exception as e:
        st.error(f"Error loading JSON: {e}")
        return pd.DataFrame()

df = load_data()

if df.empty:
    st.warning("DataFrame is empty. Checking file structure...")
else:
    st.success(f"Successfully loaded {len(df)} rows!")
    st.write("Columns found in your JSON:", list(df.columns))
    st.dataframe(df.head(3))
