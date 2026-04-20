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
from data_fetcher import add_new_workout

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
    """Displays a formatted social media post."""

    with st.container(border=True):

        # Header
        col_img, col_text = st.columns([1, 9])

        with col_img:
            if user_image:
                st.image(user_image, width=55)

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

        # Caption
        st.write(content)

        # Post image
        if post_image:
            st.image(post_image, use_column_width=True)

        # Actions row
        like_col, comment_col, spacer, save_col = st.columns([1, 1, 6, 1])

        with like_col:
            st.markdown("⭐")

        with comment_col:
            st.markdown("💬")

        with save_col:
            st.markdown(
                "<div style='text-align:right'>🔖</div>",
                unsafe_allow_html=True
            )

    st.write("")

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
        # The 'or 0' tells Python to use 0 if the database value is None
        total_calories += workout['calories_burned'] or 0
        total_distance += workout['distance'] or 0
        total_steps += workout['steps'] or 0
    
    # Display the beautiful summary UI
    st.subheader("Your Activity Summary")
    
    # Display metrics directly (so our unit test can see them!)
    st.metric(label="Total Calories", value=f"{total_calories} kcal")
    st.metric(label="Total Distance", value=f"{total_distance} km")
    st.metric(label="Total Steps", value=total_steps)


def display_recent_workouts(workouts_list):
    """Displays users workouts with information like steps walked, calories burned, total distance walked e.t.c"""
    st.subheader("Recent Workouts") # Line written by Gemini

    if not workouts_list:
        st.write("No recent workouts to display.")

    # Loop through each individual workout in the list
    for workout in workouts_list:
        with st.container(border=True): # Creates a nice box around each workout
            col1, col2 = st.columns([1, 2]) # Line written by Gemini
            
            with col1:
                # Display the date/time of this specific workout
                st.write(f"**Workout on:**") # Line written by Gemini
                st.write(workout['start_timestamp']) # Line written by Gemini
            
            with col2:
                # Use columns inside the container for the stats
                m1, m2, m3 = st.columns(3) # Line written by Gemini
                m1.metric("Distance", f"{workout['distance']} km") # Line written by Gemini
                m2.metric("Steps", workout['steps']) # Line written by Gemini
                m3.metric("Burned", f"{workout['calories_burned']} kcal") # Line written by Gemini
        
        st.write("") # Adds a small bit of spacing between containers



def display_genai_advice(timestamp, content, image): 
    """display a motivation advice by genAi
    Arguments:
    timestamp a string with time
    content a string with motivational phrase by genAI
    image a url of a motivitional image
    
    """
    st.subheader("GenAI Advice")
    
    with st.container(border=True): 
        st.caption(timestamp) 
        st.write(content) 
    if image:
        st.image(image, use_column_width=True) 


def display_dynamic_workout_form(user_id, selected_type):
    """Displays the dynamic input form based on the workout category selected."""
    
    if selected_type in ["Running", "Swimming", "Gym"]:
        st.subheader(f"Log your {selected_type} workout")

        # Common inputs for all workouts
        date = st.date_input("Date")
        start_time = st.time_input("Start Time")
        end_time = st.time_input("End Time")

        workout_data = {}

        # Render specific fields based on the selected workout
        if selected_type == "Running":
            total_time = st.number_input("Total time (minutes)", min_value=0)
            miles = st.number_input("Total miles", min_value=0.0)
            pace = st.number_input("Average pace", min_value=0.0)
            hr = st.number_input("Heart rate average", min_value=0)
            hr_pick = st.number_input("Heart rate peak", min_value=0)
            calories = st.number_input("Calories", min_value=0)

            workout_data = {
                "date": date,
                "start_time": start_time,
                "end_time": end_time,
                "total_time": total_time,
                "miles": miles,
                "pace": pace,
                "hr": hr,
                "hr_pick": hr_pick,
                "calories": calories
            }

        if selected_type == "Swimming":
            total_time = st.number_input("Total time (minutes)", min_value=0)
            miles = st.number_input("Total miles", min_value=0.0)
            pace = st.number_input("Average pace", min_value=0.0)
            hr = st.number_input("Heart rate average", min_value=0)
            hr_pick = st.number_input("Heart rate peak", min_value=0)
            calories = st.number_input("Calories", min_value=0)

            workout_data = {
                "date": date,
                "start_time": start_time,
                "end_time": end_time,
                "total_time": total_time,
                "miles": miles,
                "pace": pace,
                "hr": hr,
                "hr_pick": hr_pick,
                "calories": calories
            }

        elif selected_type == "Gym":
            exercises = [] 
            
            total_time = st.number_input("Total time (minutes)", min_value=0)
            hr = st.number_input("Heart rate average", min_value=0)
            hr_pick = st.number_input("Heart rate peak", min_value=0)
            calories = st.number_input("Calories", min_value=0)
            
            number_exercises = st.number_input("Number of exercises", min_value=1, step=1)
            
            st.write("---")
            for number in range(number_exercises):
                st.markdown(f"**Exercise {number + 1}**")
                name = st.text_input("Name of exercise", key=f"name_{number}")
                sets = st.number_input("How many sets", key=f"sets_{number}", min_value=0)
                rep = st.number_input("How many repetitions", key=f"reps_{number}", min_value=0)
                weight = st.number_input("Weight", key=f"weight_{number}", min_value=0.0)
                st.write("")
                
                exercises.append({
                    "name": name,
                    "sets": sets,
                    "reps": rep,
                    "weight": weight
                })

            workout_data = {
                "date": date,
                "start_time": start_time,
                "end_time": end_time,
                "total_time": total_time,
                "hr": hr,
                "hr_pick": hr_pick,
                "calories": calories,
                "exercises": exercises
            }

        # Save Button
        if st.button(f"Save {selected_type} Workout"):
            add_new_workout(user_id, selected_type, workout_data) 
            st.success(f"{selected_type} workout logged successfully!")
            
            # Reset the form so it disappears after saving
            st.session_state.selected_workout_type = None
            st.rerun()

    # Placeholder for Cycling and Hiking until you build them out
    elif selected_type in ["Cycling", "Hiking"]:
        st.info(f"The form for {selected_type} is coming soon! Check back later.")