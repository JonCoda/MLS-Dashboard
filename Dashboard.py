import streamlit as st
import pandas as pd
import time

# --- 1. Mock Data Source ---
# In a real application, you would fetch this data from an API or by web scraping.
# For now, let's simulate some MLS match data.
def get_mls_scores():
    """
    Simulates fetching MLS match scores.
    In a real application, this function would make an API call or scrape a website.
    """
    scores = [
        {"home_team": "Atlanta United FC", "away_team": "Inter Miami CF", "home_score": 2, "away_score": 1, "status": "Final"},
        {"home_team": "LA Galaxy", "away_team": "LAFC", "home_score": 0, "away_score": 0, "status": "Half-time"},
        {"home_team": "Seattle Sounders FC", "away_team": "Portland Timbers", "home_score": 1, "away_score": 0, "status": "25'"},
        {"home_team": "New York City FC", "away_team": "New York Red Bulls", "home_score": "-", "away_score": "-", "status": "7:30 PM EDT"},
        {"home_team": "FC Dallas", "away_team": "Houston Dynamo FC", "home_score": "-", "away_score": "-", "status": "8:30 PM EDT"},
    ]
    return pd.DataFrame(scores)

# --- 2. Streamlit Application ---

st.set_page_config(
    page_title="MLS Scoreboard Dashboard",
    page_icon="⚽",
    layout="centered",
    initial_sidebar_state="expanded",
)

st.title("⚽ MLS Scoreboard Dashboard")

st.write("---") # Separator for better aesthetics

# --- 3. Dashboard Layout ---

# Create a placeholder for the live scores, so we can update it later for auto-refresh
score_placeholder = st.empty()

# This is a simple auto-refresh mechanism. For a more robust solution,
# you might use st.experimental_rerun() or background threads/scheduling if needed.
# For now, we'll simulate a loop with a sleep to show the refresh concept.
while True:
    with score_placeholder.container():
        st.header("Latest Scores")
        current_scores = get_mls_scores()
        
        # Display scores in a clear format
        for index, row in current_scores.iterrows():
            col1, col2, col3 = st.columns([2, 1, 2]) # Adjust column widths as needed
            with col1:
                st.markdown(f"**{row['home_team']}**")
            with col2:
                st.markdown(f"**{row['home_score']} - {row['away_score']}**")
            with col3:
                st.markdown(f"**{row['away_team']}**")
            st.write(f"<small>{row['status']}</small>", unsafe_allow_html=True)
            st.write("---") # Separator between matches

        st.info(f"Last updated: {time.strftime('%Y-%m-%d %H:%M:%S EDT')}")
        
    # Refresh every 30 seconds (you can adjust this)
    time.sleep(30)
