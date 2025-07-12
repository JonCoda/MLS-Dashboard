import streamlit as st
import pandas as pd
import requests
import time
import os
from datetime import datetime # To get current date for fixtures

# --- Configuration for API-Sports Football API ---
# Get your API key securely.
# 1. Best for deployment: Use Streamlit's secrets management.
#    Create a `.streamlit/secrets.toml` file in your project:
#    [api]
#    mls_key = "YOUR_ACTUAL_API_KEY_HERE"
# 2. For local testing (less secure for sharing): Environment variable.
#    Before running `streamlit run your_app.py`, in your terminal:
#    export MLS_API_KEY="YOUR_ACTUAL_API_KEY_HERE"
# 3. Direct in code (ONLY for temporary testing, DO NOT SHARE or deploy like this!):
#    MLS_API_KEY = "YOUR_ACTUAL_API_KEY_HERE"

try:
    API_KEY = st.secrets["api"]["mls_key"]
except (AttributeError, KeyError):
    API_KEY = os.getenv("MLS_API_KEY", "ba48316d0bc6c7d57e7415942bcb70b0")

# API-Sports Football API details
# The base URL for API-Sports Football API is typically this.
# While you mentioned api-sports.b-cdn.net, the API access is usually via this host.
API_BASE_URL = "https://v3.football.api-sports.io/"
FIXTURES_ENDPOINT = "fixtures"
MLS_LEAGUE_ID = 253 # API-Sports ID for Major League Soccer
CURRENT_SEASON = datetime.now().year # Get the current year for the season

# --- Function to fetch MLS scores from API-Sports Football API ---
def get_mls_scores_from_api_sports():
    """
    Fetches MLS match scores from the API-Sports Football API.
    """
    headers = {
        "x-apisports-key": API_KEY # API-Sports typically uses this header for authentication
    }

    # Parameters for fetching today's fixtures for MLS
    params = {
        "league": MLS_LEAGUE_ID,
        "season": CURRENT_SEASON,
        "date": datetime.now().strftime("%Y-%m-%d"), # Get today's date in YYYY-MM-DD format
        # You could also use "live": "all" to get all live matches regardless of date,
        # but for a dashboard focusing on current/upcoming, filtering by date is common.
        "timezone": "America/New_York" # Adjust timezone as needed for fixture times
    }

    try:
        api_url = f"{API_BASE_URL}{FIXTURES_ENDPOINT}"
        
        response = requests.get(api_url, headers=headers, params=params, timeout=15)
        response.raise_for_status() # Raise HTTPError for bad responses (4xx or 5xx)

        data = response.json()
        
        matches_data = []

        # Check if 'response' key exists and is a list (common API-Sports structure)
        if "response" in data and isinstance(data["response"], list):
            for match in data["response"]:
                # Extracting data based on API-Sports Football API JSON structure
                
                # Teams
                home_team_name = match.get("teams", {}).get("home", {}).get("name", "N/A")
                away_team_name = match.get("teams", {}).get("away", {}).get("name", "N/A")

                # Scores (handle different statuses: full-time, live, not started)
                home_score = match.get("score", {}).get("fulltime", {}).get("home", "-")
                away_score = match.get("score", {}).get("fulltime", {}).get("away", "-")

                # If match is live, get current goals
                if match.get("fixture", {}).get("status", {}).get("short") in ["1H", "HT", "2H", "ET", "P", "BT"]:
                     home_score = match.get("goals", {}).get("home", 0)
                     away_score = match.get("goals", {}).get("away", 0)

                # Status
                status_short = match.get("fixture", {}).get("status", {}).get("short", "N/A")
                status_elapsed = match.get("fixture", {}).get("status", {}).get("elapsed")
                fixture_date_time = match.get("fixture", {}).get("date")

                display_status = status_short
                if status_short == "FT":
                    display_status = "Final"
                elif status_short == "HT":
                    display_status = "Half-time"
                elif status_short in ["1H", "2H", "ET", "P", "BT"] and status_elapsed is not None:
                    display_status = f"{status_elapsed}'" # Display minutes elapsed for live games
                elif status_short == "NS" and fixture_date_time:
                    try:
                        # Convert ISO format date to a more readable time
                        dt_object = datetime.fromisoformat(fixture_date_time.replace('Z', '+00:00'))
                        display_status = dt_object.strftime("%I:%M %p %Z").replace("AM EDT", "AM").replace("PM EDT", "PM") # Format to HH:MM AM/PM
                    except ValueError:
                        display_status = "Scheduled"
                elif status_short == "PST":
                    display_status = "Postponed"
                elif status_short == "CANC":
                    display_status = "Cancelled"
                elif status_short == "AET":
                    display_status = "AET" # After Extra Time
                elif status_short == "PEN":
                    display_status = "Penalties" # Penalties in progress


                matches_data.append({
                    "home_team": home_team_name,
                    "away_team": away_team_name,
                    "home_score": home_score,
                    "away_score": away_score,
                    "status": display_status
                })
        else:
            st.warning("No 'response' key or unexpected data format in API response. Check API-Sports documentation for fixture structure.")
            st.json(data) # Show raw data for debugging
            return pd.DataFrame()

        return pd.DataFrame(matches_data)

    except requests.exceptions.RequestException as e:
        st.error(f"Error connecting to API-Sports: {e}. Check your internet connection or API status.")
        if response.status_code == 401:
            st.error("Unauthorized: Your API key might be invalid or missing.")
        elif response.status_code == 403:
            st.error("Forbidden: You might not have access to this resource or hit rate limits.")
        elif response.status_code == 404:
            st.error("Not Found: Check the API URL and endpoint.")
        return pd.DataFrame()
    except Exception as e:
        st.error(f"An unexpected error occurred while processing API-Sports data: {e}")
        # Consider st.json(data) here for debugging if it's a parsing issue
        return pd.DataFrame()

# --- Streamlit Dashboard Layout ---

st.set_page_config(
    page_title="MLS Scoreboard",
    page_icon="⚽",
    layout="centered",
)

st.title("⚽ MLS Scoreboard Dashboard (API-Sports)")
st.write("---")

# Placeholder for dynamic content updates
score_display_area = st.empty()

# Loop to refresh the scores
while True:
    with score_display_area.container():
        st.header("Latest MLS Scores")
        
        current_scores = get_mls_scores_from_api_sports()
        
        if not current_scores.empty:
            if not current_scores.empty:
                # Sort to show live/upcoming matches first if needed, then by time
                # You might need more sophisticated sorting based on fixture_date_time if you have it.
                
                for index, row in current_scores.iterrows():
                    col1, col2, col3 = st.columns([2, 1, 2])
                    with col1:
                        st.markdown(f"**{row['home_team']}**")
                    with col2:
                        st.markdown(f"**{row['home_score']} - {row['away_score']}**")
                    with col3:
                        st.markdown(f"**{row['away_team']}**")
                    st.write(f"<small>{row['status']}</small>", unsafe_allow_html=True)
                    st.write("---")
            else:
                st.info("No MLS matches found for today. Check back later or adjust date parameters.")
        else:
            st.info("No scores available right now or an API error occurred. Trying again soon...")

        st.markdown(f"**Last updated:** {time.strftime('%Y-%m-%d %H:%M:%S EDT')}")
        
    # Wait before refreshing again (API-Sports free plan is 100 requests/day, so be mindful)
    # 60 seconds (1 minute) is 60 requests/hour * 24 hours = 1440 requests/day.
    # This is fine for their free tier if you don't refresh too often.
    time.sleep(60) # Refresh every 60 seconds (1 minute)
