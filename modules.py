#############################################################################
# modules.py
#
# This file contains modules that may be used throughout the app.
#############################################################################

from internals import create_component
import streamlit as st


def display_my_custom_component(value):
    """Displays a 'my custom component'."""
    data = {'NAME': value}
    html_file_name = "my_custom_component"
    create_component(data, html_file_name)


def display_post(username, user_image, timestamp, content, post_image):
    """Displays a formatted social media post."""

    with st.container(border=True):

        # Header
        col_img, col_text = st.columns([1, 9])

        with col_img:
            if user_image:
                try:
                    st.image(user_image, width=55)
                except Exception:
                    st.markdown("👤")

        with col_text:
            name_col, time_col = st.columns([6, 4])

            with name_col:
                st.markdown(f"**{username}**")

            with time_col:
                st.markdown(
                    f"<div style='text-align:right'>{timestamp}</div>",
                    unsafe_allow_html=True
                )

        st.divider()

        # Content
        if content and content != "None":
            st.write(content)
        else:
            st.caption("_(no caption)_")

        # Post image — gracefully skip broken URLs
        if post_image and post_image != "None":
            try:
                st.image(post_image, use_column_width=True)
            except Exception:
                pass

        # Actions row with stat counts
        like_col, comment_col, spacer, save_col = st.columns([1, 1, 6, 1])

        with like_col:
            st.markdown("⭐ 0")

        with comment_col:
            st.markdown("💬 0")

        with save_col:
            st.markdown(
                "<div style='text-align:right'>🔖</div>",
                unsafe_allow_html=True
            )

    st.write("")


def display_activity_summary(workouts_list):
    if not workouts_list:
        st.write("No activity to summarize yet!")
        return

    total_calories = 0
    total_distance = 0
    total_steps = 0

    for workout in workouts_list:
        total_calories += workout['calories_burned'] or 0
        total_distance += workout['distance'] or 0
        total_steps += workout['steps'] or 0

    st.subheader("Your Activity Summary")

    st.metric(label="Total Calories", value=f"{total_calories} kcal")
    st.metric(label="Total Distance", value=f"{total_distance} km")
    st.metric(label="Total Steps", value=total_steps)


def display_recent_workouts(workouts_list):
    """Displays users workouts with steps, calories, distance."""
    st.subheader("Recent Workouts")

    if not workouts_list:
        st.write("No recent workouts to display.")

    for workout in workouts_list:
        with st.container(border=True):
            col1, col2 = st.columns([1, 2])

            with col1:
                st.write(f"**Workout on:**")
                st.write(workout['start_timestamp'])

            with col2:
                m1, m2, m3 = st.columns(3)
                m1.metric("Distance", f"{workout['distance']} km")
                m2.metric("Steps", workout['steps'])
                m3.metric("Burned", f"{workout['calories_burned']} kcal")

        st.write("")


def display_genai_advice(timestamp, content, image):
    """Display a motivational advice by GenAI."""
    st.subheader("GenAI Advice")

    with st.container(border=True):
        st.caption(timestamp)
        st.write(content)

    if image:
        try:
            st.image(image, use_column_width=True)
        except Exception:
            pass
