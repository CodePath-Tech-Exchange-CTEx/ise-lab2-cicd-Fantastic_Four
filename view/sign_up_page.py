import streamlit as st

# Import only the specific backend logic needed
from data_fetcher import create_user

# Import our new UI component
from modules import display_signup_form

def sign_up_page():
    st.title("Join WebFit 💪")
    
    # ==========================================
    # 1. View: Display the form and grab inputs
    # ==========================================
    name, username, password, dob, image, submitted = display_signup_form()
    
    # ==========================================
    # 2. Controller: Process the new user
    # ==========================================
    if submitted:
        # Pass the extracted variables into your backend function
        create_user(name, username, password, dob, image)
        st.success("Account successfully created! You can now log in.")