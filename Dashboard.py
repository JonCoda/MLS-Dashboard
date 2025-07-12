import streamlit as st
import pandas as pd
import requests
import time
import os
from datetime import datetime

# --- Configuration for API-Sports Football API ---
# Get your API key. Instructions for secrets.toml or environment variable are in comments below.
try:
    API_KEY = st.secrets["api"]["mls_key"]
except (AttributeError, KeyError):
    API_KEY = os.getenv("ba48316d0bc6c7d57e7415942bcb70b0") # Replace or use secrets

# API-Sports Football API details
API_BASE_URL = "https://v3.football.api-sports.io/"
FIXTURES_ENDPOINT = "fixtures"

# --- Function to fetch MLS scores from API-Sports ---
def get_mls_scores():
    """
    Fetches MLS match scores from API-Sports Football API for today.
    """
    headers = {"x-apisports-key": API_KEY}
    }

    try:
        response = requests.get(f"{API_BASE_URL}{FIXTURES_ENDPOINT}", headers=headers, params=params, timeout=10)
        response.raise_for_status() # Check for HTTP errors

        data = response.json()
        matches = []

        if "response" in data and isinstance(data["response"], list):
            for match in data["response"]:
                home_team = match["teams"]["home"]["name"]
                away_team = match["teams"]["away"]["name"]

                # Get scores based on match status
                status_short = match["fixture"]["status"]["short"]
                home_score = "-"
                away_score = "-"

                if status_short in ["FT", "AET", "PEN"]:
                    home_score = match["score"]["fulltime"]["home"]
                    away_score = match["score"]["fulltime"]["away"]
                elif status_short in ["1H", "HT", "2H", "ET", "P", "BT"]:
                    home_score = match["goals"]["home"]
                    away_score = match["goals"]["away"]

                # Format status for display
                display_status = status_short
                if status_short == "FT": display_status = "Final"
                elif status_short == "HT": display_status = "Half-time"
                elif status_short in ["1H", "2H", "ET", "P", "BT"]:
                    display_status = f"{match['fixture']['status']['elapsed']}'"
                elif status_short == "NS":
                    # Format kickoff time
                    kickoff_dt = datetime.fromisoformat(match["fixture"]["date"].replace('Z', '+00:00'))
                    display_status = kickoff_dt.strftime("%I:%M %p").replace("AM EDT", "AM").replace("PM EDT", "PM")

                matches.append({
                    "home_team": home_team,
                    "away_team": away_team,
                    "home_score": home_score,
                    "away_score": away_score,
                    "status": display_status
                })
        return pd.DataFrame(matches)

    except requests.exceptions.RequestException as e:
        st.error(f"Error fetching scores: {e}")
        return pd.DataFrame()
    except KeyError as e:
        st.error(f"Missing data in API response: {e}. Check API structure.")
        # st.json(data) # Uncomment for debugging raw API response
        return pd.DataFrame()
    except Exception as e:
        st.error(f"An unexpected error occurred: {e}")
        return pd.DataFrame()

# --- Streamlit App ---

st.set_page_config(
    page_title="MLS Scoreboard",
    page_icon="⚽",
    layout="centered",
)

st.title("⚽ MLS Scoreboard")
st.write("---")

score_placeholder = st.empty()

while True:
    with score_placeholder.container():
        st.header("Today's MLS Matches")
        
        if not scores_df.empty:
            for _, row in scores_df.iterrows():
                col1, col2, col3 = st.columns([2, 1, 2])
                with col1: st.markdown(f"**{row['home_team']}**")
                with col2: st.markdown(f"**{row['home_score']} - {row['away_score']}**")
                with col3: st.markdown(f"**{row['away_team']}**")
                st.write(f"<small>{row['status']}</small>", unsafe_allow_html=True)
                st.write("---")
        else:
            st.info("No MLS matches found for today, or an error occurred.")

        st.info(f"Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S EDT')}")
        
    time.sleep(60) # Refresh every 60 seconds
