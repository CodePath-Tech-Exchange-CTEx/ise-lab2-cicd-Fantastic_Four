#############################################################################
# modules.py
#
# This file contains modules that may be used throughout the app.
#
# You will write these in Unit 2. Do not change the names or inputs of any
# function other than the example.
#############################################################################

from internals import create_component
import streamlit as st # import streamlit

# This one has been written for you as an example. You may change it as wanted.
def display_my_custom_component(value):
    """Displays a 'my custom component' which showcases an example of how custom
    components work.

    value: the name you'd like to be called by within the app
    """
    # Define any templated data from your HTML file. The contents of
    # 'value' will be inserted to the templated HTML file wherever '{{NAME}}'
    # occurs. You can add as many variables as you want.
    data = {
        'NAME': value,
    }
    # Register and display the component by providing the data and name
    # of the HTML file. HTML must be placed inside the "custom_components" folder.
    html_file_name = "my_custom_component"
    create_component(data, html_file_name)


def display_post(username, user_image, timestamp, content, post_image):
    """Write a good docstring here."""
    pass


def display_activity_summary(workouts_list):
    # The Guard Clause - updated to use the correct variable name
    if not workouts_list:
        st.write("No activity to summarize yet!")
        return

    # Set up our starting variables
    total_calories = 0
    total_distance = 0
    total_steps = 0

    # Aggregate the data from the list 
    for workout in workouts_list: 
        total_calories += workout['calories_burned']
        total_distance += workout['distance']
        total_steps += workout['steps']
    
    # Display the beautiful summary UI
    st.subheader("Your Activity Summary")
    
    # Display metrics directly (so our unit test can see them!)
    st.metric(label="Total Calories", value=f"{total_calories} kcal")
    st.metric(label="Total Distance", value=f"{total_distance} km")
    st.metric(label="Total Steps", value=total_steps)


def display_recent_workouts(workouts_list):
    """Write a good docstring here."""
    pass


def display_genai_advice(timestamp, content, image):
    """Write a good docstring here."""
    pass
