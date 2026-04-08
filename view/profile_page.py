import streamlit as st

# Import our backend functions and UI modules
from data_fetcher import get_user_profile, get_user_workouts
from modules import display_recent_workouts

def show_profile_page(user_id):
    st.title("My Profile 👤")
    
    # 1. Fetch the data
    user_profile = get_user_profile(user_id)
    user_workouts = get_user_workouts(user_id)
    
    # 2. Extract the info
    full_name = user_profile["full_name"]
    username = user_profile["username"]
    profile_image = user_profile["profile_image"]
    friends_list = user_profile["friends"]
    
    # 3. Display the top section
    st.image(profile_image, width=150)
    st.subheader(full_name)
    st.write(f"@{username} | {len(friends_list)} friends")
    
    st.divider()
    
    # 4. Display the workouts
    display_recent_workouts(user_workouts)