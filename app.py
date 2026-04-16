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
    create_user,
    add_new_workout
)

from view.community_page import show_community_page
from view.activity_page import show_activity_page
from view.sign_up_page import sign_up_page
from view.loggin_page import login_page
from view.home_page import home_page
from view.profile_page import show_profile_page
from view.add_workout_page import show_add_workout_page


if __name__ == '__main__':

    if 'logged_in_user' not in st.session_state:
        # The user isn't logged in yet, so show them the tabs!
        login_tab, signup_tab = st.tabs(["Login", "Sign Up"])
        
        with login_tab:
            login_page()
                    
        with signup_tab:
            # Notice how this lines up exactly with "with login_tab:" !
            sign_up_page()      
                
    else:
       # --- THIS IS YOUR MAIN APP ---
        USER_ID = st.session_state['logged_in_user']

        if 'next_page' in st.session_state:
            st.session_state.navigation_radio = st.session_state.next_page
            del st.session_state.next_page 

        st.sidebar.title("Navigation")
        
        
        page_selection = st.sidebar.radio(
            "Go to:", 
            ["Home", "Community Feed", "Activity Dashboard", "Add Workout", "My Profile"],
            key="navigation_radio" 
        )
        # Route the app based on what the user clicks
        if page_selection == "Home":
            home_page(USER_ID) 
        elif page_selection == "Community Feed":
            show_community_page(USER_ID)
        elif page_selection == "Activity Dashboard":
            show_activity_page(USER_ID)
        elif page_selection == "Add Workout":
            show_add_workout_page(USER_ID)
        elif page_selection == "My Profile":
            show_profile_page(USER_ID)

        # --- LOGOUT BUTTON GOES HERE ---
        st.sidebar.divider() # Add a nice line above the logout button
        if st.sidebar.button("Logout"):
            del st.session_state['logged_in_user']
            st.rerun() # Refresh the page to kick them back to the login screen