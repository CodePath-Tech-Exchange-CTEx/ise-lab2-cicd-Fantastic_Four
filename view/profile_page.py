import streamlit as st

# Import our backend functions
from data_fetcher import get_user_profile, get_user_workouts, get_streak

# Import our UI modules
from modules import display_profile_header, display_streak_details, display_recent_workouts

def show_profile_page(user_id):
    st.title("My Profile 👤")

    # ==========================================
    # 1. Controller: Fetch and Extract Data
    # ==========================================
    user_profile  = get_user_profile(user_id)
    user_workouts = get_user_workouts(user_id)
    streak_data   = get_streak(user_id)

    full_name     = user_profile.get("full_name", "")
    username      = user_profile.get("username", "")
    profile_image = user_profile.get("profile_image", "")
    friends_list  = user_profile.get("friends", [])

    current_streak = streak_data.get("current_streak", 0)

    # ==========================================
    # 2. View: Render the Page Components
    # ==========================================
    
    # 3. Top Section
    display_profile_header(full_name, username, profile_image, len(friends_list))

    st.divider()

    # 4. Streak Section
    display_streak_details(current_streak)

    st.divider()

    # 5. Recent Workouts Section
    display_recent_workouts(user_workouts)