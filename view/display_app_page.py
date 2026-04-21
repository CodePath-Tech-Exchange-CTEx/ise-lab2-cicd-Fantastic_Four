"""
this function is NOT called in the main yet.
I was trying to have display_app_page() function in a single file
to have everything more organized.
"""
import streamlit as st
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
    verify_login
)

def display_app_page(user_id):
    st.title('Welcome to SDS!')

    value = st.text_input('Enter your name:')
    display_my_custom_component(value)

    st.divider()

    user_workouts = get_user_workouts(user_id)
    user_posts = get_user_posts(user_id)
    genai_info = get_genai_advice(user_id)

    display_genai_advice(
        genai_info['timestamp'],
        genai_info['content'],
        genai_info['image']
    )

    st.write("")

    display_activity_summary(user_workouts)
    display_recent_workouts(user_workouts)

    st.divider()

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
