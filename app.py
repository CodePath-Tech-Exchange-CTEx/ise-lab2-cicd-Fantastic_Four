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
    get_user_workouts,
    verify_login,
    create_user
)
from community_page import show_community_page
from activity_page import show_activity_page
from data_fetcher import verify_login
from sign_up_page import sign_up_page
# from display_app_page import display_app_page


def display_app_page():
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

    if 'logged_in_user' not in st.session_state:
        # The user isn't logged in yet, so show them the tabs!
        login_tab, signup_tab = st.tabs(["Login", "Sign Up"])
        
        with login_tab:
            st.title("Login to SDS Fitness")
            
            # 1. The UI
            Username = st.text_input("Enter your Username:")
            password = st.text_input("Enter your password", type="password")
            
            # 2. The Button & Validation
            if st.button("Login"):
                fetched_user_id = verify_login(Username, password)

                if fetched_user_id is not None:
                    # 3. Giving the wristband!
                    st.session_state['logged_in_user'] = fetched_user_id
                    st.success("Login successful! Welcome!")
                    st.rerun() # Tells Streamlit to refresh the page immediately
                else:
                    st.error("Incorrect username or password.")
                    
        with signup_tab:
            # Notice how this lines up exactly with "with login_tab:" !
            sign_up_page()      
                
    else:
        # --- THIS IS YOUR MAIN APP ---
        USER_ID = st.session_state['logged_in_user']

        # Create a menu in the sidebar
        st.sidebar.title("Navigation")
        
        page_selection = st.sidebar.radio("Go to:", ["Home", "Community Feed", "Activity Dashboard"])
        
        # Route the app based on what the user clicks
        if page_selection == "Home":
            display_app_page() 
        elif page_selection == "Community Feed":
            show_community_page(USER_ID)
        elif page_selection == "Activity Dashboard":
            show_activity_page(USER_ID)

        # --- LOGOUT BUTTON GOES HERE ---
        st.sidebar.divider() # Add a nice line above the logout button
        if st.sidebar.button("Logout"):
            del st.session_state['logged_in_user']
            st.rerun() # Refresh the page to kick them back to the login screen