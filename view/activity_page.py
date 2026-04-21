import streamlit as st

# Import our backend functions
from data_fetcher import get_user_workouts, get_user_workout_dates, get_all_calendar_events

# Import the UI components
from modules import (
    display_activity_summary, 
    display_recent_workouts, 
    display_training_calendar, 
    display_share_progress
)

def show_activity_page(user_id):
    st.title("My Activity Dashboard 🏃‍♂️")

    # 1. Fetch all required data for the page
    user_workouts = get_user_workouts(user_id)
    workout_dates = get_user_workout_dates(user_id)
    calendar_events = get_all_calendar_events(user_id)

    # 2. Render Activity Summary
    display_activity_summary(user_workouts)
    st.divider()

    # 3. Render The Calendar Feature
    display_training_calendar(calendar_events)
    st.divider()

    # 4. Render Recent Workouts
    display_recent_workouts(user_workouts)
    st.divider()

    # 5. Render The "Share" Button Feature
    display_share_progress(user_id, user_workouts)