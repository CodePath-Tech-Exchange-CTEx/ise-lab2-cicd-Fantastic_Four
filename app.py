#############################################################################
# app.py
#
# This file contains the entrypoint for the app.
#############################################################################

import streamlit as st

# Local module imports
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
    get_user_workouts
)
from community_page import show_community_page
from activity_page import show_activity_page

# Global Constants
USER_ID = 'user1'


def display_app_page():
    """Displays the home page of the app."""
    st.title('Welcome to SDS!')
    
    # --- 1. Custom Component Example ---
    value = st.text_input('Enter your name:')
    display_my_custom_component(value)
    
    st.divider() # Adds a nice visual break on the screen

    # --- 2. Fetch All Data ---
    # Grouping data fetching makes the code easier to read and maintain
    user_workouts = get_user_workouts(USER_ID)
    user_posts = get_user_posts(USER_ID)
    genai_info = get_genai_advice(USER_ID)
    
    # --- 3. Display UI Components ---
    
    # Display AI Advice
    display_genai_advice(
        genai_info['timestamp'], 
        genai_info['content'], 
        genai_info['image']
    )
    
    st.write("") # Quick spacer
    
    # Display Workout Summaries
    display_activity_summary(user_workouts)
    display_recent_workouts(user_workouts)
    
    st.divider()
    
    # Display User Posts
    st.subheader("Your Posts")
    if not user_posts:
        st.write("No posts to display yet.")
    else:
        for post in user_posts:
            display_post(
                post['username'], 
                post['user_image'], 
                post['timestamp'], 
                post['content'], 
                post['post_image']
            )


if __name__ == '__main__':
    # 1. Create a menu in the sidebar
    st.sidebar.title("Navigation")
    
    # FIX 1: Add "Activity Dashboard" to the list of options here!
    page_selection = st.sidebar.radio("Go to:", ["Home", "Community Feed", "Activity Dashboard"])
    
    # 2. Route the app based on what the user clicks
    if page_selection == "Home":
        display_app_page() 
    elif page_selection == "Community Feed":
        show_community_page(USER_ID)
    elif page_selection == "Activity Dashboard":
        # FIX 2: Use the uppercase USER_ID variable
        show_activity_page(USER_ID)