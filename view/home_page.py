import streamlit as st

from modules import (
    display_my_custom_component, 
    display_post, 
    display_genai_advice, 
    display_activity_summary, 
    display_recent_workouts
)
from data_fetcher import (
    get_user_posts, 
    get_genai_advice, 
    get_user_profile, 
    get_user_sensor_data, 
    get_user_workouts,
    verify_login,
    create_user
)

def home_page(USER_ID):
    # Fetch real user data
    profile = get_user_profile(USER_ID)
    user_name = profile.get('full_name', 'User')

    # --- 1. Custom CSS (Kept from your snippet) ---
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


    # --- 3. Main Header ---
    st.title(f"Welcome {user_name}")
    st.write("Don't forget to log a physical activity today")
    st.write("##") 

    # --- 4. Horizontal Activity Grid ---
    cols = st.columns(6)
    activities = [
        ("Cycling", "🚲"), ("Hiking", "🥾"), ("Runnning", "🏃"), 
        ("Swimming", "🏊"), ("Yoga", "🧘")
    ]

    for i, (name, icon) in enumerate(activities):
        with cols[i]:
            st.markdown(f'<div class="activity-card"><span style="font-size: 40px;">{icon}</span></div>', unsafe_allow_html=True)
            # This button records the activity in your database
            if st.button(f"Log {name}", key=f"btn_{name}"):
                # Here you would call a backend function like:
                # create_activity(USER_ID, name)
                st.success(f"Logged {name}!")

    # --- 5. Add Activity ---
    with cols[5]:
        st.markdown('<div class="activity-card"><span style="font-size: 30px; font-weight: bold;">+</span></div>', unsafe_allow_html=True)
        if st.button("New", key="add_new"):
            st.write("New Activity")

    st.divider()