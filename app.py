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
home_ats_col = "Home \nTeam \nATS %"
away_ats_col = "Away \nTeam\nATS %"
ml_prob_col = "ML Win \nProbability"
best_bet_col = "Best Bet \nRecommendation"
parlay_signal_col = "SIGNAL\nMoneyline \nParlay"

if not df.empty:
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
        # Filter for your new parlay and value tiers
        valid_parlays = ["🔥 PRIME PARLAY", "⭐ ML PARLAY", "RISKY ML VALUE"]
        df = df[df[parlay_signal_col].isin(valid_parlays)]

    st.markdown(f"**Showing {len(df)} active games**")
    st.divider()

    def fmt_signed(val):
        try:
            f = float(val)
            return f"+{f:.2f}" if f > 0 else f"{f:.2f}"
        except (ValueError, TypeError):
            return val if val is not None else "N/A"

    def fmt_inverse(val):
        try:
            f = -float(val)
            return f"+{f:.2f}" if f > 0 else f"{f:.2f}"
        except (ValueError, TypeError):
            return "N/A"

    def fmt_pct(val):
        try:
            return f"{float(val) * 100:.1f}%"
        except (ValueError, TypeError):
            return val if val is not None else "N/A"

    for _, row in df.iterrows():
        home = row.get(home_col, 'Home')
        away = row.get(away_col, 'Away')
        
        # Spreads & Projections for both sides
        v_spread_home = row.get(spread_col)
        home_spread = fmt_signed(v_spread_home)
        away_spread = fmt_inverse(v_spread_home)

        m_proj_home = row.get(proj_col)
        home_proj = fmt_signed(m_proj_home)
        away_proj = fmt_inverse(m_proj_home)

        m_edge = fmt_signed(row.get(edge_col))
        ml_prob = fmt_pct(row.get(ml_prob_col))
        home_ats = fmt_pct(row.get(home_ats_col))
        away_ats = fmt_pct(row.get(away_ats_col))
        
        best_bet = row.get(best_bet_col, 'NO PLAY')
        if pd.isna(best_bet) or str(best_bet).strip() == '':
            best_bet = 'NO PLAY'

        parlay_signal = row.get(parlay_signal_col, 'NO PLAY')
        if pd.isna(parlay_signal) or str(parlay_signal).strip() == '':
            parlay_signal = 'NO PLAY'

        # Style tag color based on parlay tier
        signal_bg = "rgba(31, 41, 55, 0.5)"
        signal_color = "#9ca3af"
        if "PRIME PARLAY" in parlay_signal:
            signal_bg = "rgba(16, 185, 129, 0.1)"
            signal_color = "#34d399"
        elif "ML PARLAY" in parlay_signal:
            signal_bg = "rgba(59, 130, 246, 0.1)"
            signal_color = "#60a5fa"
        elif "RISKY ML VALUE" in parlay_signal:
            signal_bg = "rgba(245, 158, 11, 0.1)"
            signal_color = "#fbbf24"

        st.markdown(f"""
            <div class="card">
                <div style="font-size: 1.1rem; font-weight: bold; margin-bottom: 8px;">{away} @ {home}</div>
                <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 8px; font-size: 0.9rem; color: #9ca3af;">
                    <div>Vegas Spread ({away}): <b style="color:#f3f4f6;">{away_spread}</b></div>
                    <div>Vegas Spread ({home}): <b style="color:#f3f4f6;">{home_spread}</b></div>
                    <div>Model Proj ({away}): <b style="color:#f3f4f6;">{away_proj}</b></div>
                    <div>Model Proj ({home}): <b style="color:#f3f4f6;">{home_proj}</b></div>
                    <div>Model Edge: <b style="color:#60a5fa;">{m_edge}</b></div>
                    <div>ML Win Prob ({home}): <b style="color:#34d399;">{ml_prob}</b></div>
                    <div>ATS ({away}): <b style="color:#f3f4f6;">{away_ats}</b></div>
                    <div>ATS ({home}): <b style="color:#f3f4f6;">{home_ats}</b></div>
                </div>
                <div style="margin-top: 12px; padding-top: 8px; border-top: 1px solid #1f2937; font-size: 0.85rem; display: flex; justify-content: space-between; align-items: center;">
                    <div>Best Bet: <span style="background: rgba(16, 185, 129, 0.1); color: #34d399; padding: 2px 6px; border-radius: 4px; font-weight: bold;">{best_bet}</span></div>
                    <div>ML Signal: <span style="background: {signal_bg}; color: {signal_color}; padding: 2px 6px; border-radius: 4px; font-weight: bold;">{parlay_signal}</span></div>
                </div>
            </div>
        """, unsafe_allow_html=True)
