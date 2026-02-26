#############################################################################
# app.py
#
# This file contains the entrypoint for the app.
#
#############################################################################

import streamlit as st
from modules import display_my_custom_component, display_post, display_genai_advice, display_activity_summary, display_recent_workouts
from data_fetcher import get_user_posts, get_genai_advice, get_user_profile, get_user_sensor_data, get_user_workouts

userId = 'user1'


def display_app_page():
    """Displays the home page of the app."""
    st.title('Welcome to SDS!')

    # An example of displaying a custom component called "my_custom_component"
    value = st.text_input('Enter your name')
    display_my_custom_component(value)

    # get user posts
  user_posts = get_user_posts(userId)

    st.subheader("Recent Posts")
    
    if user_posts:
        for post in user_posts:
            display_post(post['user_profile']['username'], post['user_profile']['profile_image'], post['timestamp'], post['content'], post['post_image'])
    else:
        st.write("No posts available.")

    # Fetch the workout data for the user
    user_workouts = get_user_workouts(userId)
    
    # Call your function to display it on the screen!
    display_activity_summary(user_workouts)
    # function to display user workout
    display_recent_workouts(user_workouts)
    #function to display the genAI advice
    GenAI_info= get_genai_advice(userId)
    display_genai_advice(GenAI_info['timestamp'], GenAI_info['content'], GenAI_info['image'])

# This is the starting point for your app. You do not need to change these lines
if __name__ == '__main__':
    display_app_page()
