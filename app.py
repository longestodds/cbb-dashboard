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

# Exact column names from your Google Sheet
home_col = "Home Team"
away_col = "Away Team"
spread_col = "Spread \n(Home Team)\n(column B)"
proj_col = "Model Spread \n(Home Team Column B)"
edge_col = "Model Edge\nGreen Favors Home\nBlue Favors Away"
ml_prob_col = "ML Win \nProbability"
best_bet_col = "Best Bet \nRecommendation"

if not df.empty:
    # Drop empty/blank rows to fix the 999 count issue
    df = df.dropna(subset=[home_col, away_col])
    df = df[df[home_col].astype(str).str.strip() != ""]
    df = df[df[away_col].astype(str).str.strip() != ""]
    df = df[~df[home_col].astype(str).str.lower().isin(['nan', 'none', ''])]

if df.empty:
    st.warning("Waiting for active games data...")
else:
    search = st.text_input("🔍 Search Team", placeholder="Type team name...")
    filter_choice = st.radio("Filter View", ["All Games", "🔥 Top Plays", "🎯 ML Parlays"], horizontal=True)

    if search and not df.empty:
        df = df[df[home_col].str.contains(search, case=False, na=False) | df[away_col].str.contains(search, case=False, na=False)]
    
    if filter_choice == "🔥 Top Plays" and not df.empty:
        df = df[df[best_bet_col].notna() & (df[best_bet_col].astype(str).str.strip() != '') & (df[best_bet_col] != 'NO PLAY')]
    elif filter_choice == "🎯 ML Parlays" and not df.empty:
        df['temp_prob'] = pd.to_numeric(df[ml_prob_col], errors='coerce')
        df = df[df['temp_prob'] >= 0.80]

    st.markdown(f"**Showing {len(df)} active games**")
    st.divider()

    def fmt(val):
        try:
            return f"{float(val):.2f}"
        except (ValueError, TypeError):
            return val if val is not None else "N/A"

    for _, row in df.iterrows():
        home = row.get(home_col, 'Home')
        away = row.get(away_col, 'Away')
        v_spread = fmt(row.get(spread_col))
        m_proj = fmt(row.get(proj_col))
        m_edge = fmt(row.get(edge_col))
        ml_prob = fmt(row.get(ml_prob_col))
        best_bet = row.get(best_bet_col, 'NO PLAY')
        if pd.isna(best_bet) or str(best_bet).strip() == '':
            best_bet = 'NO PLAY'

        st.markdown(f"""
            <div class="card">
                <div style="font-size: 1.1rem; font-weight: bold; margin-bottom: 8px;">{away} @ {home}</div>
                <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 8px; font-size: 0.9rem; color: #9ca3af;">
                    <div>Vegas Spread ({home}): <b style="color:#f3f4f6;">{v_spread}</b></div>
                    <div>Model Proj ({home}): <b style="color:#f3f4f6;">{m_proj}</b></div>
                    <div>Model Edge: <b style="color:#60a5fa;">{m_edge}</b></div>
                    <div>ML Win Prob ({home}): <b style="color:#34d399;">{ml_prob}</b></div>
                </div>
                <div style="margin-top: 12px; padding-top: 8px; border-top: 1px solid #1f2937; font-size: 0.85rem;">
                    Best Bet: <span style="background: rgba(16, 185, 129, 0.1); color: #34d399; padding: 2px 6px; border-radius: 4px; font-weight: bold;">{best_bet}</span>
                </div>
            </div>
        """, unsafe_allow_html=True)
