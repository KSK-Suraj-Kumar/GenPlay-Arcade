import streamlit as st
import pandas as pd
import mysql.connector
import plotly.express as px
from streamlit_extras.metric_cards import style_metric_cards
import time

# Redirect to Login if not authenticated
if "logged_in" not in st.session_state or not st.session_state.logged_in:
        st.warning("You must log in first!")
        time.sleep(3)
        st.switch_page("login.py")

# ---------- CONFIGURATION ----------
st.set_page_config(page_title="User Dashboard", page_icon="📊", layout="wide")

# ---------- BACKGROUND & STYLES ----------
def apply_custom_styles():
    st.markdown("""
        <style>
        /* Background for the entire app */
        .stApp {
            background: linear-gradient(to right, #01b3ef, #2e5caf);
            background-size: cover;
            background-position: center;
            background-attachment: fixed;
            color: white;
        }

        /* Container padding */
        .block-container {
            padding-top: 2rem;
            padding-bottom: 2rem;
        }

        /* Metric container custom styles */
        div[data-testid="metric-container"] {
            background-color: #00008b; /* Dark box background */
            border: 1px solid #5e17eb;
            border-radius: 15px;
            padding: 20px;
            box-shadow: 0 0 12px rgba(94, 23, 235, 0.4);
        }

        /* Hover effect */
        div[data-testid="metric-container"]:hover {
            border: 1px solid #7b37ff;
            box-shadow: 0 0 20px rgba(123, 55, 255, 0.6);
            transform: scale(1.02);
        }

        /* Metric label */
        div[data-testid="metric-container"] > label {
            color: #00008b;
            font-size: 18px;
            font-weight: 600;
        }

        /* Metric value */
        div[data-testid="metric-container"] > div {
            color: #00008b;
            font-size: 36px;
            font-weight: bold;
        }

        /* Buttons */
        .stButton > button {
            background-color: #4CAF50;
            color: white;
            border-radius: 10px;
            padding: 0.5rem 1.2rem;
            font-weight: bold;
            border: none;
        }

        .stButton > button:hover {
            background-color: #ffffff;
            color: green;
            transform: scale(1.05);
        }
        </style>
    """, unsafe_allow_html=True)

apply_custom_styles()

# ---------- DATABASE CONNECTION ----------
def get_db_connection():
    return mysql.connector.connect(
        host="localhost",
        user="root",        
        password="PASSWORD",    # Replace with your password
        database="genplayarcade"     
    )

# ---------- FETCH DATA ----------
@st.cache_data(ttl=60)
def fetch_scores():
    conn = get_db_connection()
    query = "SELECT username, score, date_played FROM snake_game_scores ORDER BY score DESC"
    df = pd.read_sql(query, conn)
    conn.close()
    return df

data = fetch_scores()

current_user = st.session_state.username

# ---------- DASHBOARD HEADER ----------
st.markdown("<h1 style='text-align: center;'>🎓 GenPlay Arcade User Dashboard</h1>", unsafe_allow_html=True)
st.markdown("---")

# ---------- KPI METRICS ----------
user_data = data[data['username'] == current_user]

total_users = data['username'].nunique()
highest_score = data['score'].max()
total_games = data.shape[0]

col1, col2, col3 = st.columns(3)
with col1:
    st.metric("👥 Total Players", f"{total_users}")
with col2:
    st.metric("🏆 Highest Score", f"{highest_score}")
with col3:
    st.metric("🎮 Games Played", f"{total_games}")

# ---------- USER SCORES TABLE ----------
st.subheader("🏅 Leaderboard")
st.dataframe(data[['username', 'score', 'date_played']].head(10), use_container_width=True)

# ---------- CHARTS ----------
col1, col2 = st.columns(2)

top_users = data.groupby('username')['score'].max().reset_index().sort_values(by='score', ascending=False).head(10)

# Bar Chart
fig_bar = px.bar(
    top_users,
    x='username',
    y='score',
    title="Top 10 Users by Score",
    color='score',
    color_continuous_scale='plasma',
    template='plotly_dark'
)
col1.plotly_chart(fig_bar, use_container_width=True)

# Line Chart for current user
if not user_data.empty:
    fig_line = px.line(
        user_data,
        x='date_played',
        y='score',
        title=f"📈 {current_user}'s Score Progression",
        markers=True,
        template='plotly_dark'
    )
    fig_line.update_traces(line=dict(color="#7b37ff", width=3))
    col2.plotly_chart(fig_line, use_container_width=True)
else:
    col2.info(f"No game data found for {current_user}!")

# ---------- PIE CHART ----------
st.subheader("📊 Score Distribution")

bins = [0, 20, 40, 60, 80, 100]
labels = ['0-20', '21-40', '41-60', '61-80', '81-100+']
data['score_range'] = pd.cut(data['score'], bins=bins, labels=labels, include_lowest=True)

pie_data = data['score_range'].value_counts().reset_index()
pie_data.columns = ['Score Range', 'Count']

fig_pie = px.pie(
    pie_data,
    values='Count',
    names='Score Range',
    title='Score Distribution by Range',
    template='plotly_dark',
    color_discrete_sequence=px.colors.sequential.Plasma
)

st.plotly_chart(fig_pie, use_container_width=True)

if st.button("⬅️Back"):
    st.switch_page("login.py")

# ---------- FOOTER ----------
st.markdown("---")
st.markdown("<h6 style='text-align: center; color: black;'>© 2025 GenPlay Arcade</h6>", unsafe_allow_html=True)
