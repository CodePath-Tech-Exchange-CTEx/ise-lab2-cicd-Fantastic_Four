import streamlit as st
import streamlit as st

# Local module imports
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
    get_user_sensor_data, 
    get_user_workouts,
    verify_login,
    create_user,
    add_new_workout
)


def show_add_workout_page(user_id):
    
    st.title("Add a New Workout")

    date = st.date_input("Date")

    start_time = st.time_input("Start Time")
    end_time = st.time_input("End Time")

    workout_type = st.selectbox("Label", ["Running", "Swimming", "Gym"])

    workout_data = {}

    if workout_type == "Running":
        total_time = st.number_input("Total time")
        miles = st.number_input("total miles")
        pace = st.number_input("average pace")
        hr = st.number_input("heart rate average")
        hr_pick = st.number_input("heart rate pick")
        calories = st.number_input("calories")

        current_exercise = {
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

        workout_data = current_exercise

    elif workout_type == "Swimming":
        total_time = st.number_input("Total time")
        miles = st.number_input("total miles")
        pace = st.number_input("average pace")
        hr = st.number_input("heart rate average")
        hr_pick = st.number_input("heart rate pick")
        calories = st.number_input("calories")

        current_exercise = {
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

        workout_data = current_exercise

    elif workout_type == "Gym":
        exercises = [] # Start with an empty list
        
        total_time = st.number_input("Total time")
        hr = st.number_input("heart rate average")
        hr_pick = st.number_input("heart rate pick")
        calories = st.number_input("calories")
        
        number_exercises = st.number_input("number of exercises", min_value=1, step=1)
        
        for number in range(number_exercises):
            # 1. Get the inputs (Don't forget the unique keys!)
            name = st.text_input("Name of exercise", key=f"name_{number}")
            sets = st.number_input("How many sets", key=f"sets_{number}")
            rep = st.number_input("How many repetitions", key=f"reps_{number}")
            weight = st.number_input("Weight", key=f"weight_{number}")
            
            # 2. Bundle them into a dictionary
            current_exercise = {
                "name": name,
                "sets": sets,
                "reps": rep,
                "weight": weight
            }
            
            # 3. Add to our main list
            exercises.append(current_exercise)

        current_workout = {
            "date": date,
            "start_time": start_time,
            "end_time": end_time,
            "total_time": total_time,
            "hr": hr,
            "hr_pick": hr_pick,
            "calories": calories,
            "exercises": exercises
        }

        workout_data = current_workout


    if st.button("Save Workout"):
        add_new_workout(user_id, workout_type, workout_data) 



