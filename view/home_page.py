import streamlit as st

from modules import (
    display_my_custom_component,
    display_post,
    display_genai_advice,
    display_activity_summary,
    display_recent_workouts,
    display_dynamic_workout_form,
    display_streak_badge
)

from data_fetcher import (
    get_user_posts,
    get_genai_advice,
    get_user_profile,
    get_user_workouts,
    verify_login,
    create_user,
    add_new_workout,
    get_streak
)

def home_page(USER_ID):
    # Fetch real user data
    profile = get_user_profile(USER_ID)
    user_name = profile.get('full_name', 'User')

    # --- Streak Badge (top-right corner) ---
    streak_data = get_streak(USER_ID)
    display_streak_badge(streak_data.get('current_streak', 0))

    # session state
    # to track the button clicked
    if 'selected_workout_type' not in st.session_state:
        st.session_state.selected_workout_type = None

    # --- Custom CSS ---
    st.markdown("""
        <style>
        .activity-card {
            background-color: #D9D9D9;
            border-radius: 15px;
            height: 100px; width: 100px;
            display: flex; align-items: center; justify-content: center;
            margin: 0 auto; transition: 0.3s;
        }
        .activity-card:hover { background-color: #BDBDBD; }
        .activity-label { text-align: center; font-size: 14px; margin-top: 8px; color: #333; }
        </style>
    """, unsafe_allow_html=True)


    # --- Main Header ---
    st.title(f"Hello {user_name}")
    st.write("Don't forget to log a physical activity today")
    st.write("##") 

    # --- Horizontal Activity Grid ---
    cols = st.columns(6)
    activities = [
        ("Cycling", "🚲"), ("Hiking", "🥾"), ("Running", "🏃"), 
        ("Swimming", "🏊"), ("Gym", " 🏋️"), ("New Activity", "➕")
    ]

    for i, (name, icon) in enumerate(activities):
        with cols[i]:
            st.markdown(f'<div class="activity-card"><span style="font-size: 40px;">{icon}</span></div>', unsafe_allow_html=True)
            
            # This button Updates session state
            if st.button(f"Log {name}", key=f"btn_{name}"):
                st.session_state.selected_workout_type = name

        
            

    st.divider()

    # --- Dynamic Workout Form ---
    # Check if a button was clicked, then call the function from modules.py
    selected_type = st.session_state.selected_workout_type
    
    if selected_type:
        display_dynamic_workout_form(USER_ID, selected_type)