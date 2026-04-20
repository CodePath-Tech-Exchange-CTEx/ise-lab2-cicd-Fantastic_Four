import streamlit as st

from data_fetcher import (
    get_user_posts, 
    get_genai_advice, 
    get_user_profile,  
    get_user_workouts,
    verify_login,
    create_user
)

def sign_up_page():
    with st.form("signup_form"):
        st.subheader("Create a New Account")
        
        name = st.text_input("Enter your name")
        username = st.text_input("Enter your unique username")
        password = st.text_input("Create a unique password", type="password")
        dob = st.date_input("Insert your DOB")
        image = st.text_input("Upload your profile picture (URL)")   

        submit_button = st.form_submit_button("Sign Up")
        
        if submit_button:
            # Call your awesome backend function!
            create_user(name, username, password, dob, image)
            st.success("Account successfully created! You can now log in.")