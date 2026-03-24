#############################################################################
# app.py
#
# This file contains the entrypoint for the app.
#
#############################################################################

import streamlit as st
from modules import display_my_custom_component, display_post, display_genai_advice, display_activity_summary, display_recent_workouts
from data_fetcher import get_user_posts, get_genai_advice, get_user_profile, get_user_sensor_data, get_user_workouts

from community_page import show_community_page

userId = 'user1'


def display_app_page():
    """Displays the home page of the app."""
    st.title('Welcome to SDS!')
    
    # An example of displaying a custom component called "my_custom_component"
    value = st.text_input('Enter your name:')
    display_my_custom_component(value)
    

    # if user_posts:
    # for post in user_posts:
    #     display_post(post['username'], post['user_image'], post['timestamp'], post['content'], post['post_image'])
        
    # Fetch the workout data for the user
    user_workouts = get_user_workouts(userId)

    # Get user post data
    user_posts = get_user_posts(userId)
    
    # - debug info. don't uncomment in final deployment
    #st.write(user_posts)
    
    # - debug info. don't uncomment in final deployment
    # st.write("DEBUG WORKOUTS:", user_workouts)
    
    # Call your function to display it on the screen!
    for post in user_posts:
        display_post(post['username'], post['user_image'], post['timestamp'], post['content'], post['post_image'])
    display_activity_summary(user_workouts)
    # function to display user workout
    display_recent_workouts(user_workouts)
    #function to display the genAI advice
    GenAI_info= get_genai_advice(userId)
    
    # - debug info. don't uncomment in final deployment
    # st.write("DEBUG GENAI:", GenAI_info)
    
    display_genai_advice(GenAI_info['timestamp'], GenAI_info['content'], GenAI_info['image'])


if __name__ == '__main__':
    # 1. Create a menu in the sidebar
    st.sidebar.title("Navigation")
    page_selection = st.sidebar.radio("Go to:", ["Home", "Community Feed"])
    
    # 2. Route the app based on what the user clicks
    if page_selection == "Home":
        display_app_page() # Shows your original app.py stuff
    elif page_selection == "Community Feed":
        show_community_page(userId) # Shows your brand new community feed!