#############################################################################
# modules.py
#
# This file contains modules that may be used throughout the app.
#############################################################################

from internals import create_component
import streamlit as st # import streamlit
from data_fetcher import add_new_workout

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
        st.info("🏃‍♂️ No activity to summarize yet! Head over to the Home page to log your first workout.")
        return

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

    st.metric(label="Total Calories", value=f"{round(total_calories)} kcal")
    st.metric(label="Total Distance", value=f"{total_distance} km")
    st.metric(label="Total Steps", value=total_steps)


def display_recent_workouts(workouts_list):
    """Displays users workouts with steps, calories, distance."""
    st.subheader("Recent Workouts")

    if not workouts_list:
        st.write("No recent workouts to display.")

    for workout in workouts_list[:3]:
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

    with st.expander("More..."):
        for workout in workouts_list[3:]:
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
        st.image(image, use_column_width=True) 


def display_dynamic_workout_form(user_id, selected_type):
    """Displays the dynamic input form based on the workout category selected."""
    
    if selected_type in ["Running", "Swimming", "Gym"]:
        st.subheader(f"Log your {selected_type} workout")

        # Common inputs for all workouts side-by-side (Date removed)
        col_start, col_end = st.columns(2)
        with col_start:
            start_time = st.time_input("Start Time")
        with col_end:
            end_time = st.time_input("End Time")

        workout_data = {}

        # Render specific fields based on the selected workout
        if selected_type in ["Running", "Swimming"]:
            col1, col2 = st.columns(2)
            
            with col1:
                total_time = st.number_input("Total time (minutes)", min_value=0)
                pace = st.number_input("Average pace", min_value=0.0)
                hr = st.number_input("Heart rate average", min_value=0)
                
            with col2:
                miles = st.number_input("Total miles", min_value=0.0)
                calories = st.number_input("Calories", min_value=0)
                hr_peak = st.number_input("Heart rate peak", min_value=0)

            workout_data = {
                "start_time": start_time,
                "end_time": end_time,
                "total_time": total_time,
                "miles": miles,
                "pace": pace,
                "hr": hr,
                "hr_peak": hr_peak, 
                "calories": calories
            }

        elif selected_type == "Gym":
            exercises = [] 
            
            col1, col2 = st.columns(2)
            with col1:
                total_time = st.number_input("Total time (minutes)", min_value=0)
                hr = st.number_input("Heart rate average", min_value=0)
            with col2:
                calories = st.number_input("Calories", min_value=0)
                hr_peak = st.number_input("Heart rate peak", min_value=0)
            
            number_exercises = st.number_input("Number of exercises", min_value=1, step=1)
            
            st.write("---")
            for number in range(number_exercises):
                # Use an expander for each exercise to keep the UI clean
                with st.expander(f"**Exercise {number + 1}**", expanded=True):
                    name = st.text_input("Name of exercise", key=f"name_{number}")
                    
                    # Nest columns inside the expander for sets, reps, and weight
                    col_sets, col_reps, col_weight = st.columns(3)
                    with col_sets:
                        sets = st.number_input("Sets", key=f"sets_{number}", min_value=0)
                    with col_reps:
                        rep = st.number_input("Reps", key=f"reps_{number}", min_value=0)
                    with col_weight:
                        weight = st.number_input("Weight", key=f"weight_{number}", min_value=0.0)
                
                exercises.append({
                    "name": name,
                    "sets": sets,
                    "reps": rep,
                    "weight": weight
                })

            workout_data = {
                "start_time": start_time,
                "end_time": end_time,
                "total_time": total_time,
                "hr": hr,
                "hr_peak": hr_peak,
                "calories": calories,
                "exercises": exercises
            }

        st.write("")

        # Save Button
        if st.button(f"Save {selected_type} Workout", use_container_width=True):
            add_new_workout(user_id, selected_type, workout_data) 
            st.success(f"{selected_type} workout logged successfully!")
            
            # Reset the form so it disappears after saving
            st.session_state.selected_workout_type = None
            st.rerun()

    # Placeholder for Cycling and Hiking until you build them out
    elif selected_type in ["Cycling", "Hiking"]:
        st.info(f"The form for {selected_type} is coming soon! Check back later.")