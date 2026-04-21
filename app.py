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

from view.ai_plan_page import show_ai_plan_page


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
       # --- MAIN APP ---
        USER_ID = st.session_state['logged_in_user']

        if 'next_page' in st.session_state:
            st.session_state.navigation_radio = st.session_state.next_page
            del st.session_state.next_page 

        # --- Sidebar Styling ---
        # We target Streamlit's internal HTML elements using their data-testid attributes.
        # `stSidebar` wraps the whole sidebar. The radio options use `stRadio` labels.
        # The selected radio item gets a highlighted pill via the :has() CSS selector,
        # which checks if a hidden radio input inside the label is checked.
        st.markdown("""
            <style>
            [data-testid="stSidebar"] {
                background-color: #1a1a2e;
                padding-top: 2rem;
            }
            [data-testid="stSidebar"] * {
                color: #e0e0e0 !important;
            }
            [data-testid="stSidebar"] .stRadio label {
                display: block;
                padding: 10px 16px;
                border-radius: 10px;
                margin-bottom: 4px;
                font-size: 15px;
                transition: background 0.2s;
                cursor: pointer;
            }
            [data-testid="stSidebar"] .stRadio label:hover {
                background-color: rgba(255,255,255,0.08);
            }
            [data-testid="stSidebar"] .stRadio label:has(input:checked) {
                background-color: #e94560;
                color: white !important;
                font-weight: 600;
            }
            [data-testid="stSidebar"] .stRadio [data-testid="stMarkdownContainer"] p {
                font-size: 13px;
                opacity: 0.6;
                margin-bottom: 8px;
            }
            [data-testid="stSidebar"] hr {
                border-color: rgba(255,255,255,0.15);
            }
            [data-testid="stSidebar"] .stButton button {
                width: 100%;
                background-color: transparent;
                border: 1px solid rgba(255,255,255,0.25);
                color: #e0e0e0 !important;
                border-radius: 10px;
                transition: background 0.2s;
            }
            [data-testid="stSidebar"] .stButton button:hover {
                background-color: rgba(255,255,255,0.08);
                border-color: rgba(255,255,255,0.4);
            }
            </style>
        """, unsafe_allow_html=True)

        st.sidebar.title("Navigation")

        # Icons are added directly to the label strings.
        # The if/elif routing below must match these strings exactly.
        page_selection = st.sidebar.radio(
            "Go to:",
            ["🏠  Home", "👥  Community Feed", "📊  Activity Dashboard", "🤖  AI Coach Plan", "👤  My Profile"],
            key="navigation_radio"
        )

        if page_selection == "🏠  Home":
            home_page(USER_ID)
        elif page_selection == "👥  Community Feed":
            show_community_page(USER_ID)
        elif page_selection == "📊  Activity Dashboard":
            show_activity_page(USER_ID)
        elif page_selection == "🤖  AI Coach Plan":
            show_ai_plan_page(USER_ID)
        elif page_selection == "👤  My Profile":
            show_profile_page(USER_ID)

        st.sidebar.divider()
        if st.sidebar.button("⏻  Logout"):
            del st.session_state['logged_in_user']
            st.rerun()