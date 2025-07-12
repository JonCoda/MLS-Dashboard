import streamlit as st
import pandas as pd
import requests # New import for making API calls
import time
import os # For environment variables (good practice for API keys)

# --- Configuration for API (Replace with your actual API details) ---
# It's best practice to store sensitive information like API keys
# as environment variables or using Streamlit's secrets management.
# For local testing, you can set it directly, but remove for deployment.

# Example of setting an environment variable (in your terminal before running):
# export MLS_API_KEY="your_actual_api_key_here"
# OR
# In Streamlit, create a .streamlit/secrets.toml file:
# [api]
# mls_key = "your_actual_api_key_here"

# Replace with the actual base URL of your chosen MLS API
# This is a placeholder. For example, it might be something like:
# "https://api.sportmonks.com/v3/football/" or "https://api-sports.io/football/v3/"
MLS_API_BASE_URL = "https://api-football-v1.p.rapidapi.com/v2/leagues/league/{253}" # REPLACE THIS!
MLS_API_ENDPOINT = "fixtures" # REPLACE THIS with the endpoint for live matches/fixtures
MLS_LEAGUE_ID = "253" # REPLACE THIS with the actual League ID for MLS from your chosen API
# You'll likely need to consult the API documentation for correct IDs and endpoints.

# Get API key from Streamlit secrets or environment variable
try:
    MLS_API_KEY = st.secrets["api"]["mls_key"]
except (AttributeError, KeyError):
    MLS_API_KEY = os.getenv("MLS_API_KEY", "YOUR_API_KEY_HERE") # Fallback for local testing. REMEMBER TO REPLACE!

# --- Function to fetch MLS scores from a hypothetical API ---
def get_mls_scores_from_api():
    """
    Fetches MLS match scores from a hypothetical API.
    You will need to adapt this function to the specific API you choose.
    """
    headers = {
        "Accept": "application/json"
        # Some APIs might require the API key in headers, e.g., "x-rapidapi-key": MLS_API_KEY
    }
    params = {
        "api_token": 'ba48316d0bc6c7d57e7415942bcb70b0', # Common way to pass API key, but check your API's docs
        "league_id": '253',
        "date": time.strftime("%Y-%m-%d") # Fetch today's matches, or use a 'live' endpoint
        # Add other parameters as per your API's documentation (e.g., 'timezone', 'include')
    }

    try:
        # Construct the full URL. E.g., https://api.example.com/mls/fixtures
        api_url = f"{MLS_API_BASE_URL}{MLS_API_ENDPOINT}"
        
        st.write(f"<small>Attempting to fetch from: {api_url} with params: {params}</small>", unsafe_allow_html=True) # For debugging
        
        response = requests.get(api_url, headers=headers, params=params, timeout=10) # Added timeout
        response.raise_for_status() # Raise an HTTPError for bad responses (4xx or 5xx)

        data = response.json()
        
        # --- IMPORTANT: Parse the API response according to its structure ---
        # This part is highly dependent on the API you use.
        # Below is a hypothetical parsing based on common API structures.
        
        matches = []
        
        # Hypothetical structure: data['data'] contains a list of matches
        if 'data' in data and isinstance(data['data'], list):
            for match in data['data']:
                home_team_name = match.get('home_team', {}).get('name', 'N/A')
                away_team_name = match.get('away_team', {}).get('name', 'N/A')
                
                # Check for score presence and handle live vs. scheduled matches
                home_score = match.get('scores', {}).get('home_score', '-')
                away_score = match.get('scores', {}).get('away_score', '-')
                
                status_long = match.get('status', {}).get('long', 'N/A')
                status_short = match.get('status', {}).get('short', 'N/A')
                
                # Try to get a more descriptive status if available
                display_status = status_long if status_long != 'N/A' else status_short

                # A simplified way to represent status for the dashboard
                if display_status == "Finished":
                    display_status = "Final"
                elif display_status == "Halftime":
                    display_status = "Half-time"
                elif display_status in ["Not Started", "NS"]:
                    # Try to get kickoff time if available
                    kickoff_time = match.get('time', {}).get('starting_at', {}).get('time', '')
                    if kickoff_time:
                        display_status = kickoff_time # Or format it better: f"Kickoff: {kickoff_time}"
                    else:
                        display_status = "Scheduled"
                # For live matches, the status might be a minute count (e.g., "25'") or "Live"
                # If your API provides a minute, you can use it.
                elif 'minute' in match and match['minute'] is not None:
                     display_status = f"{match['minute']}'"
                
                matches.append({
                    "home_team": home_team_name,
                    "away_team": away_team_name,
                    "home_score": home_score,
                    "away_score": away_score,
                    "status": display_status
                })
        else:
            st.warning("API response did not contain expected 'data' key or it was not a list.")
            return pd.DataFrame() # Return empty DataFrame on unexpected structure

        return pd.DataFrame(matches)

    except requests.exceptions.HTTPError as e:
        st.error(f"HTTP Error fetching data: {e}. Check your API key, endpoint, and parameters.")
        if response.status_code == 401:
            st.error("Unauthorized: Your API key might be invalid or missing.")
        elif response.status_code == 403:
            st.error("Forbidden: You might not have access to this resource or hit rate limits.")
        elif response.status_code == 404:
            st.error("Not Found: Check the API URL and endpoint.")
        return pd.DataFrame()
    except requests.exceptions.ConnectionError as e:
        st.error(f"Connection Error: Could not connect to the API. Check your internet connection or the API server status. Details: {e}")
        return pd.DataFrame()
    except requests.exceptions.Timeout:
        st.error("Request Timeout: The API took too long to respond.")
        return pd.DataFrame()
    except requests.exceptions.RequestException as e:
        st.error(f"An unexpected error occurred while making API request: {e}")
        return pd.DataFrame()
    except Exception as e:
        st.error(f"An error occurred while processing API data: {e}")
        st.json(data) # Show the raw data for debugging
        return pd.DataFrame()


# --- Streamlit Application ---

st.set_page_config(
    page_title="MLS Scoreboard Dashboard",
    page_icon="⚽",
    layout="centered",
    initial_sidebar_state="expanded",
)

st.title("⚽ MLS Scoreboard Dashboard")

st.write("---") # Separator for better aesthetics

# --- Dashboard Layout ---

# Create a placeholder for the live scores
score_placeholder = st.empty()

# This loop will continuously fetch and display data
while True:
    with score_placeholder.container():
        st.header("Latest Scores")
        
        # Call the API fetching function
        current_scores = get_mls_scores_from_api()
        
        if not current_scores.empty:
            # Display scores in a clear format
            for index, row in current_scores.iterrows():
                col1, col2, col3 = st.columns([2, 1, 2]) # Adjust column widths
                with col1:
                    st.markdown(f"**{row['home_team']}**")
                with col2:
                    st.markdown(f"**{row['home_score']} - {row['away_score']}**")
                with col3:
                    st.markdown(f"**{row['away_team']}**")
                st.write(f"<small>{row['status']}</small>", unsafe_allow_html=True)
                st.write("---") # Separator between matches
        else:
            st.info("No MLS match data available or an error occurred. Please check configuration and API status.")

        st.info(f"Last updated: {time.strftime('%Y-%m-%d %H:%M:%S EDT')}")
        
    # Refresh every 30 seconds (adjust based on API rate limits and desired refresh rate)
    time.sleep(30)
