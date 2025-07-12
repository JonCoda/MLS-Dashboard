import streamlit as st
import pandas as pd
import requests
import time
import os
from datetime import datetime

# --- Configuration for API-Sports Football API ---
# Get your API key.
# Recommended: Create a .streamlit/secrets.toml file in your project:
# [api]
# mls_key = "YOUR_ACTUAL_API_KEY_HERE"
# Alternative for local testing (less secure for sharing): Environment variable.
# Before running `streamlit run your_app.py`, in your terminal:
# export MLS_API_KEY="YOUR_ACTUAL_API_KEY_HERE"
#
# DO NOT hardcode your API key directly in 'os.getenv' default value for deployment!

try:
    API_KEY = st.secrets["api"]["mls_key"]
except (AttributeError, KeyError):
    # This is where you would get the environment variable named 'MLS_API_KEY'
    API_KEY = os.getenv("MLS_API_KEY", "ba48316d0bc6c7d57e7415942bcb70b0
") # <-- Corrected

# API-Sports Football API details
API_BASE_URL = "https://v3.football.api-sports.io/"
FIXTURES_ENDPOINT = "fixtures"
MLS_LEAGUE_ID = 253 # <-- Re-added
CURRENT_SEASON = datetime.now().year # <-- Re-added

# --- Function to fetch MLS scores from API-Sports ---
def get_mls_scores():
    """
    Fetches MLS match scores from API-Sports Football API for today.
    """
    headers = {"x-apisports-key": API_KEY}

    # --- Corrected: Define params dictionary here ---
    params = {
        "league": MLS_LEAGUE_ID,
        "season": CURRENT_SEASON,
        "date": datetime.now().strftime("%Y-%m-%d"),
        "timezone": "America/New_York"
    }

    try:
        response = requests.get(f"{API_BASE_URL}{FIXTURES_ENDPOINT}", headers=headers, params=params, timeout=10)
        response.raise_for_status() # Check for HTTP errors

        data = response.json()
        matches = []

        if "response" in data and isinstance(data["response"], list):
            for match in data["response"]:
                # Ensure all necessary keys exist before accessing, or use .get()
                # Simplified access, assumes keys exist as per typical API-Sports response
                home_team = match["teams"]["home"]["name"]
                away_team = match["teams"]["away"]["name"]

                status_short = match["fixture"]["status"]["short"]
                home_score = "-"
                away_score = "-"

                if status_short in ["FT", "AET", "PEN"]:
                    # These keys are often missing if match is not yet finished
                    home_score = match["score"].get("fulltime", {}).get("home", "-")
                    away_score = match["score"].get("fulltime", {}).get("away", "-")
                elif status_short in ["1H", "HT", "2H", "ET", "P", "BT"]:
                    home_score = match["goals"].get("home", "-") # Use .get() for safety
                    away_score = match["goals"].get("away", "-") # Use .get() for safety

                display_status = status_short
                if status_short == "FT": display_status = "Final"
                elif status_short == "HT": display_status = "Half-time"
                elif status_short in ["1H", "2H", "ET", "P", "BT"]:
                    elapsed = match["fixture"]["status"].get("elapsed")
                    display_status = f"{elapsed}'" if elapsed is not None else status_short
                elif status_short == "NS":
                    fixture_date_str = match["fixture"].get("date")
                    if fixture_date_str:
                        try:
                            # Safely parse date and format time
                            kickoff_dt = datetime.fromisoformat(fixture_date_str.replace('Z', '+00:00'))
                            # Format time to HH:MM AM/PM without timezone name
                            display_status = kickoff_dt.strftime("%I:%M %p").lstrip('0') # lstrip to remove leading 0 from hour
                            if display_status.startswith(':'): display_status = '12' + display_status # Handle 12:xx AM/PM
                        except ValueError:
                            display_status = "Scheduled"
                    else:
                        display_status = "Scheduled" # Fallback if date is missing
                elif status_short == "PST": display_status = "Postponed"
                elif status_short == "CANC": display_status = "Cancelled"
                elif status_short == "SUSP": display_status = "Suspended"
                elif status_short == "INT": display_status = "Interrupted"
                elif status_short == "TBD": display_status = "To Be Determined"
                elif status_short == "WO": display_status = "Walkover" # Added more specific status handling

                matches.append({
                    "home_team": home_team,
                    "away_team": away_team,
                    "home_score": home_score,
                    "away_score": away_score,
                    "status": display_status
                })
            # Add a check here for no matches returned for today
            if not matches:
                st.info("No MLS matches scheduled for today.")
        else:
            st.warning("API response did not contain expected 'response' key or it was empty.")
            # For debugging, you might want to print the raw API response
            # st.json(data)
            return pd.DataFrame() # Return empty DataFrame on unexpected structure

        return pd.DataFrame(matches)

    except requests.exceptions.RequestException as e:
        st.error(f"Network or API error: {e}. Please check your internet connection or API status.")
        # Attempt to get HTTP status code for more specific error messages
        if hasattr(e, 'response') and e.response is not None:
            if e.response.status_code == 401:
                st.error("Authentication Error (401): Invalid or missing API key. Please check your 'mls_key' in secrets.toml or environment variable.")
            elif e.response.status_code == 403:
                st.error("Forbidden (403): You might have exceeded your API rate limit or do not have access to this resource.")
            elif e.response.status_code == 404:
                st.error("Not Found (404): Check the API_BASE_URL and FIXTURES_ENDPOINT.")
            else:
                st.error(f"HTTP Error {e.response.status_code}: {e.response.text}")
        return pd.DataFrame()
    except KeyError as e:
        st.error(f"Data parsing error: Missing expected key '{e}' in API response. The API response structure might have changed or you're trying to access a key that doesn't exist for a particular match. (Check your API plan/data).")
        # st.json(data) # Uncomment this to see the full problematic data structure
        return pd.DataFrame()
    except Exception as e:
        st.error(f"An unexpected error occurred during data processing: {e}")
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

# --- Corrected: The main Streamlit loop ---
while True:
    with score_placeholder.container():
        st.header("Today's MLS Matches")
        
        scores_df = get_mls_scores() # Call the function to get scores
        
        if not scores_df.empty:
            for _, row in scores_df.iterrows():
                col1, col2, col3 = st.columns([2, 1, 2])
                with col1: st.markdown(f"**{row['home_team']}**")
                with col2: st.markdown(f"**{row['home_score']} - {row['away_score']}**")
                with col3: st.markdown(f"**{row['away_team']}**")
                st.write(f"<small>{row['status']}</small>", unsafe_allow_html=True)
                st.write("---")
        else:
            # This message will show if get_mls_scores() returns an empty DataFrame
            # which happens on API errors or if no matches are found.
            st.info("No MLS matches found for today, or an error occurred while fetching data.")

        st.info(f"Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S EDT')}")
        
    time.sleep(60) # Refresh every 60 seconds
