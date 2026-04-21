import streamlit as st

# Import the specific backend logic needed
from data_fetcher import verify_login

# Import our new UI component
from modules import display_login_form

def login_page():
    
    # ==========================================
    # 1. View: Display the form and grab inputs
    # ==========================================
    username, password, submitted = display_login_form()
            
    # ==========================================
    # 2. Controller: Validate the inputs
    # ==========================================
    if submitted:
        fetched_user_id = verify_login(username, password)

        if fetched_user_id is not None:
            # 3. State Management: Give the wristband!
            st.session_state['logged_in_user'] = fetched_user_id
            st.success("Login successful! Welcome!")
            st.rerun() # Tells Streamlit to refresh the page immediately
        else:
            st.error("Incorrect username or password.")