import streamlit as st
import pandas as pd
import requests
import time
import os # For securely getting API key

# --- Configuration (YOU MUST FILL THESE IN) ---
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

# These will come from your chosen API's documentation
API_BASE_URL = "ba48316d0bc6c7d57e7415942bcb70b0" # e.g., "https://api.sportmonks.com/v3/football/"
MLS_LEAGUE_IDENTIFIER = "253" # e.g., "1234" or "MLS"

# --- Function to fetch live MLS scores from the API ---
def get_mls_scores_from_api():
    """
    Fetches MLS match scores from a chosen API.
    You MUST adapt the API call and data parsing to your specific API's documentation.
    """
    try:
        # Define parameters for the API request
        # You'll need to check your API's documentation for the correct parameter names
        params = {
            "api_token": 'ba48316d0bc6c7d57e7415942bcb70b0',  # Common, but check your API's method (header, query param)
            "league": MLS_LEAGUE_IDENTIFIER, # How your API identifies MLS
            # Add other necessary parameters like 'date', 'status', etc.
            # Example: "date": time.strftime("%Y-%m-%d") for today's matches
        }

        # Construct the full API URL
        full_api_url = f"{API_BASE_URL}"

        # Make the GET request to the API
        response = requests.get(full_api_url, params=params, timeout=15)
        response.raise_for_status() # Raise an exception for HTTP errors (4xx or 5xx)

        # Parse the JSON response
        data = response.json()

        # --- VERY IMPORTANT: Adapt this section to your API's JSON structure ---
        # The structure of the 'data' variable (which holds the API response)
        # will be unique to each API provider. You need to inspect the 'data'
        # to correctly extract team names, scores, and status.

        # Example of how you might extract data (THIS WILL LIKELY NEED TO CHANGE)
        matches_data = []
        if "matches" in data: # Hypothetical key where match list is located
            for match in data["matches"]:
                # These keys (e.g., 'home_team_name', 'score_home') are hypothetical
                # Replace them with the actual keys from your API's JSON response
                home_team = match.get("home_team_name", "N/A")
                away_team = match.get("away_team_name", "N/A")
                home_score = match.get("score_home", "-")
                away_score = match.get("score_away", "-")
                status = match.get("match_status", "N/A") # e.g., "FULLTIME", "LIVE", "SCHEDULED"

                matches_data.append({
                    "home_team": home_team,
                    "away_team": away_team,
                    "home_score": home_score,
                    "away_score": away_score,
                    "status": status
                })
        else:
            st.warning("Could not find expected match data in API response. Check API structure.")
            st.json(data) # Display raw API response for debugging
            return pd.DataFrame()

        return pd.DataFrame(matches_data)

    except requests.exceptions.RequestException as e:
        st.error(f"Error connecting to API: {e}. Check URL, internet, and API status.")
        return pd.DataFrame()
    except Exception as e:
        st.error(f"Error processing API data: {e}.")
        # Optionally, print raw 'data' here for debugging if parsing fails
        return pd.DataFrame()

# --- Streamlit Dashboard Layout ---

st.set_page_config(
    page_title="MLS Scoreboard",
    page_icon="⚽",
    layout="centered",
)

st.title("⚽ MLS Scoreboard Dashboard")
st.write("---")

# Placeholder for dynamic content updates
score_display_area = st.empty()

# Loop to refresh the scores
while True:
    with score_display_area.container():
        st.header("Latest MLS Scores")
        
        current_scores = get_mls_scores_from_api()
        
        if not current_scores.empty:
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
            st.info("No scores available right now or API error. Trying again soon...")

        st.markdown(f"**Last updated:** {time.strftime('%Y-%m-%d %H:%M:%S EDT')}")
        
    # Wait before refreshing again (adjust based on API rate limits)
    time.sleep(60) # Refresh every 60 seconds (1 minute)
