import streamlit as st
import requests

st.set_page_config(page_title="CBB Betting Dashboard", page_icon="🏀", layout="centered")

# Custom Styling for a Clean Look
st.markdown("""
    <style>
    .stApp { background-color: #090d16; color: #f3f4f6; }
    .card { background-color: #111827; border: 1px solid #1f2937; padding: 16px; border-radius: 12px; margin-bottom: 12px; }
    </style>
""", unsafe_allow_html=True)

st.title("🏀 CBB Betting Dashboard")
st.caption("Automated daily model projections & betting edges")

# Replace with your actual deployed Apps Script Web App URL (/exec)
APPS_SCRIPT_URL = "YOUR_APPS_SCRIPT_WEB_APP_URL"

@st.cache_data(ttl=300)
def get_data():
    try:
        response = requests.get(APPS_SCRIPT_URL)
        return response.json()
    except:
        return []

data = get_data()

if not data:
    st.warning("Connecting to pipeline or awaiting data response...")
else:
    # Search & Filters
    search = st.text_input("🔍 Search Team", placeholder="Type team name...")
    
    filter_choice = st.radio("Filter View", ["All Games", "🔥 Top Plays", "🎯 ML Parlays"], horizontal=True)

    filtered_games = []
    for game in data:
        home = game.get('home_team', '')
        away = game.get('away_team', '')
        
        # Search check
        if search and search.lower() not in home.lower() and search.lower() not in away.lower():
            continue
            
        # Filter check
        best_bet = game.get('best_bet', 'NO PLAY')
        win_prob = float(game.ml_win_prob or 0)
        
        if filter_choice == "🔥 Top Plays" and best_bet == 'NO PLAY':
            continue
        if filter_choice == "🎯 ML Parlays" and win_prob < 0.80:
            continue
            
        filtered_games.append(game)

    st.markdown(f"**Showing {len(filtered_games)} games**")
    st.divider()

    for game in filtered_games:
        home = game.get('home_team', 'Home')
        away = game.get('away_team', 'Away')
        v_spread = game.get('vegas_spread', 'N/A')
        m_proj = game.get('model_projection', 'N/A')
        m_edge = game.get('model_edge', 'N/A')
        ml_prob = game.get('ml_win_prob', 'N/A')
        best_bet = game.get('best_bet', 'NO PLAY')

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
