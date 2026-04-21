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
    create_user
)

# username = st.text_input("Enter your username:")
# password = st.text_input("Enter your password", type="password")
# login_button = st.button("Login")

def login_page():
    
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