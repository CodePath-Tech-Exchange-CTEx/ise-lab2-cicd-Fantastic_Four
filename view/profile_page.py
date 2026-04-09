import streamlit as st

# Import our backend functions and UI modules
from data_fetcher import get_user_profile, get_user_workouts, get_streak
from modules import display_recent_workouts

def show_profile_page(user_id):
    st.title("My Profile 👤")

    # 1. Fetch the data
    user_profile  = get_user_profile(user_id)
    user_workouts = get_user_workouts(user_id)
    streak_data   = get_streak(user_id)

    # 2. Extract profile info
    full_name     = user_profile.get("full_name", "")
    username      = user_profile.get("username", "")
    profile_image = user_profile.get("profile_image", "")
    friends_list  = user_profile.get("friends", [])

    current_streak = streak_data.get("current_streak", 0)
    longest_streak = streak_data.get("longest_streak", 0)

    # 3. Display the top section
    if profile_image:
        st.image(profile_image, width=150)
    st.subheader(full_name)
    st.write(f"@{username} | {len(friends_list)} friends")

    st.divider()

    # 4. Streak section
    st.subheader("🔥 Workout Streak")

    col1, col2 = st.columns(2)

    with col1:
        if current_streak > 0:
            st.metric(label="Current Streak", value=f"{current_streak} 🔥")
        else:
            st.metric(label="Current Streak", value="0 😴")

    with col2:
        st.metric(label="Longest Streak", value=f"{longest_streak} 🏆")

    if current_streak == 0:
        st.info("No active streak. Log a workout to start one!")
    elif current_streak >= 7:
        st.success(f"You're on a {current_streak}-day streak! Incredible consistency 🏆")
    elif current_streak >= 3:
        st.success(f"You're on a {current_streak}-day streak! Keep it going 💪")
    else:
        st.success(f"You're on a {current_streak}-day streak! Great start 🔥")

    st.divider()

    # 5. Display recent workouts
    display_recent_workouts(user_workouts)
