import streamlit as st

# Import the UI components from modules.py
from modules import (
    display_streak_badge,
    display_activity_grid,
    display_dynamic_workout_form
)

# Import the backend functions
from data_fetcher import (
    get_user_profile,
    get_streak
)

def home_page(USER_ID):
    # ==========================================
    # 1. State Initialization
    # ==========================================
    # Track the workout button clicked
    if 'selected_workout_type' not in st.session_state:
        st.session_state.selected_workout_type = None

    # ==========================================
    # 2. Controller: Fetch Data
    # ==========================================
    profile = get_user_profile(USER_ID)
    user_name = profile.get('full_name', 'User')
    
    streak_data = get_streak(USER_ID)

    # ==========================================
    # 3. View: Render UI
    # ==========================================
    # --- Streak Badge (top-right corner) ---
    display_streak_badge(streak_data.get('current_streak', 0))

    # --- Main Header ---
    st.title(f"Hello {user_name} 👋")
    st.write("Don't forget to log a physical activity today")
    st.write("##") 

    # --- Activity Grid ---
    display_activity_grid()

    st.divider()

    # --- Dynamic Workout Form ---
    selected_type = st.session_state.selected_workout_type
    
    if selected_type:
        display_dynamic_workout_form(USER_ID, selected_type)