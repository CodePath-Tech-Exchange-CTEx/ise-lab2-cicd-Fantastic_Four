import streamlit as st

username = st.text_input("Enter your username:")
password = st.text_input("Enter your password", type="password")
login_button = st.button("Login")