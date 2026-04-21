#############################################################################
# modules.py
#
# This file acts as the UI library for the SDS Fitness app. It contains 
# all the visual Streamlit components separated from the database logic.
#############################################################################

import datetime
import streamlit as st
from streamlit_calendar import calendar

# --- Local Backend / Database Imports ---
from internals import create_component
from data_fetcher import (
    add_new_workout, 
    create_shared_post, 
    update_streak,
    schedule_ai_workout, 
    delete_workout
)


# =====================================================================
# 1. SHARED / GLOBAL COMPONENTS
# =====================================================================

def display_streak_badge(streak: int):
    """Renders a fixed-position streak badge in the top-right corner of the screen."""
    color = "#FF4500" if streak > 0 else "#9E9E9E"
    label = f"{streak} day streak" if streak != 1 else "1 day streak"

    # Injecting custom CSS to pin the badge to the top right
    st.markdown(f"""
        <style>
        .streak-badge {{
            position: fixed;
            top: 70px;
            right: 24px;
            z-index: 9999;
            background: {color};
            color: white;
            border-radius: 20px;
            padding: 8px 16px;
            display: flex;
            align-items: center;
            gap: 6px;
            font-weight: 700;
            font-size: 15px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.25);
            user-select: none;
        }}
        .streak-badge .streak-count {{
            font-size: 20px;
        }}
        </style>
        <div class="streak-badge">
            🔥 <span class="streak-count">{streak}</span> <span>{label.split(' ', 1)[1]}</span>
        </div>
    """, unsafe_allow_html=True)


def display_my_custom_component(value):
    """Displays a custom HTML/JS component using the internals module."""
    data = {'NAME': value}
    html_file_name = "my_custom_component"
    create_component(data, html_file_name)


# =====================================================================
# 2. AUTHENTICATION UI
# =====================================================================

def display_login_form():
    """Displays the login UI and returns the user inputs."""
    st.title("Login to SDS Fitness")
            
    username = st.text_input("Enter your Username:")
    password = st.text_input("Enter your password", type="password")
    
    # The button returns True when clicked
    submitted = st.button("Login")
    
    return username, password, submitted


def display_signup_form():
    """Displays the sign-up form and returns all user inputs."""
    with st.form("signup_form"):
        st.subheader("Create a New Account")
        
        name = st.text_input("Enter your name")
        username = st.text_input("Enter your unique username")
        password = st.text_input("Create a unique password", type="password")
        dob = st.date_input("Insert your DOB")
        image = st.text_input("Upload your profile picture (URL)")   

        # The button returns True only when clicked
        submitted = st.form_submit_button("Sign Up")
        
        return name, username, password, dob, image, submitted


# =====================================================================
# 3. HOME PAGE UI
# =====================================================================

def display_activity_grid():
    """Displays the horizontal grid of activity buttons and handles selection state."""
    
    # Custom CSS for the square activity buttons
    st.markdown("""
        <style>
        .activity-card {
            background-color: #D9D9D9;
            border-radius: 15px;
            height: 100px; width: 100px;
            display: flex; align-items: center; justify-content: center;
            margin: 0 auto; transition: 0.3s;
        }
        .activity-card:hover { background-color: #BDBDBD; }
        .activity-label { text-align: center; font-size: 14px; margin-top: 8px; color: #333; }
        </style>
    """, unsafe_allow_html=True)

    cols = st.columns(6)
    activities = [
        ("Cycling", "🚲"), ("Hiking", "🥾"), ("Running", "🏃"), 
        ("Swimming", "🏊"), ("Gym", " 🏋️"), ("New Activity", "➕")
    ]

    for i, (name, icon) in enumerate(activities):
        with cols[i]:
            st.markdown(f'<div class="activity-card"><span style="font-size: 40px;">{icon}</span></div>', unsafe_allow_html=True)
            
            # Clicking this button updates the global session state
            if st.button(f"Log {name}", key=f"btn_{name}"):
                st.session_state.selected_workout_type = name


# =====================================================================
# 4. WORKOUT LOGGING UI
# =====================================================================

def display_dynamic_workout_form(user_id, selected_type):
    """Displays the dynamic input form based on the workout category selected."""
    
    if selected_type in ["Running", "Swimming", "Gym", "Hiking", "Cycling"]:
        st.subheader(f"Log your {selected_type} workout")

        # Common inputs for all workouts side-by-side
        col_start, col_end = st.columns(2)
        with col_start:
            start_time = st.time_input("Start Time")
        with col_end:
            end_time = st.time_input("End Time")

        workout_data = {}

        # --- Running & Swimming Forms ---
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
                "start_time": start_time, "end_time": end_time, "total_time": total_time,
                "miles": miles, "pace": pace, "hr": hr, "hr_peak": hr_peak, "calories": calories
            }

        # --- Cycling Form ---
        elif selected_type == "Cycling":
            col1, col2 = st.columns(2)
            with col1:
                total_time = st.number_input("Total time (minutes)", min_value=0)
                miles = st.number_input("Total miles", min_value=0.0)
                avg_speed = st.number_input("Average Speed (mph)", min_value=0.0) 
            with col2:
                calories = st.number_input("Calories", min_value=0)
                hr = st.number_input("Heart rate average", min_value=0)
                bike_type = st.selectbox("Bike Type", ["Road", "Mountain", "Indoor/Spin"])

            workout_data = {
                "start_time": start_time, "end_time": end_time, "total_time": total_time,
                "miles": miles, "avg_speed": avg_speed, "calories": calories, "hr": hr, "bike_type": bike_type
            }

        # --- Hiking Form ---
        elif selected_type == "Hiking":
            col1, col2 = st.columns(2)
            with col1:
                total_time = st.number_input("Total time (minutes)", min_value=0)
                miles = st.number_input("Total miles", min_value=0.0)
                elevation_gain = st.number_input("Elevation Gain (ft)", min_value=0) 
            with col2:
                calories = st.number_input("Calories", min_value=0)
                hr = st.number_input("Heart rate average", min_value=0)
                difficulty = st.select_slider("Terrain Difficulty", options=["Easy", "Moderate", "Hard", "Extreme"])

            workout_data = {
                "start_time": start_time, "end_time": end_time, "total_time": total_time,
                "miles": miles, "elevation_gain": elevation_gain, "calories": calories, "hr": hr, "difficulty": difficulty
            }

        # --- Gym Form ---
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
            
            # Dynamically generate input fields for each exercise
            for number in range(number_exercises):
                with st.expander(f"**Exercise {number + 1}**", expanded=True):
                    name = st.text_input("Name of exercise", key=f"name_{number}")
                    
                    col_sets, col_reps, col_weight = st.columns(3)
                    with col_sets:
                        sets = st.number_input("Sets", key=f"sets_{number}", min_value=0)
                    with col_reps:
                        rep = st.number_input("Reps", key=f"reps_{number}", min_value=0)
                    with col_weight:
                        weight = st.number_input("Weight", key=f"weight_{number}", min_value=0.0)
                
                exercises.append({"name": name, "sets": sets, "reps": rep, "weight": weight})

            workout_data = {
                "start_time": start_time, "end_time": end_time, "total_time": total_time,
                "hr": hr, "hr_peak": hr_peak, "calories": calories, "exercises": exercises
            }

        st.write("")

        # Submit the form to the backend
        if st.button(f"Save {selected_type} Workout", use_container_width=True):
            add_new_workout(user_id, selected_type, workout_data) 
            st.success(f"{selected_type} workout logged successfully!")
            
            # Reset the session state so the form closes automatically
            st.session_state.selected_workout_type = None
            st.rerun()

    # Fallback for unbuilt activities
    elif selected_type in ["New Activity"]:
        st.info(f"The form for {selected_type} is coming soon! Check back later.")


# =====================================================================
# 5. ACTIVITY DASHBOARD UI
# =====================================================================

def display_activity_summary(workouts_list):
    """Displays a high-level summary of total calories, distance, and steps."""
    if not workouts_list:
        st.info("🏃‍♂️ No activity to summarize yet! Head over to the Home page to log your first workout.")
        return

    total_calories = sum(w.get('calories_burned', 0) or 0 for w in workouts_list)
    total_distance = sum(w.get('distance', 0) or 0 for w in workouts_list)
    total_steps = sum(w.get('steps', 0) or 0 for w in workouts_list)
    
    st.subheader("Your Activity Summary")
    st.metric(label="Total Calories", value=f"{round(total_calories)} kcal")
    st.metric(label="Total Distance", value=f"{total_distance} km")
    st.metric(label="Total Steps", value=total_steps)


def display_recent_workouts(workouts_list):
    """Displays a detailed list of recent workouts in expandable containers."""
    st.subheader("Recent Workouts")

    if not workouts_list:
        st.write("No recent workouts to display.")
        return

    # Show the first 3 workouts prominently
    for workout in workouts_list[:3]:
        with st.container(border=True):
            col1, col2 = st.columns([1, 2])
            with col1:
                st.write(f"**Workout on:**\n{workout['start_timestamp']}")
            with col2:
                m1, m2, m3 = st.columns(3)
                m1.metric("Distance", f"{workout['distance']} km")
                m2.metric("Steps", workout['steps'])
                m3.metric("Burned", f"{workout['calories_burned']} kcal")
        st.write("")

    # Tuck the rest inside an expander
    if len(workouts_list) > 3:
        with st.expander("More..."):
            for workout in workouts_list[3:]:
                with st.container(border=True):
                    col1, col2 = st.columns([1, 2])
                    with col1:
                        st.write(f"**Workout on:**\n{workout['start_timestamp']}")
                    with col2:
                        m1, m2, m3 = st.columns(3)
                        m1.metric("Distance", f"{workout['distance']} km")
                        m2.metric("Steps", workout['steps'])
                        m3.metric("Burned", f"{workout['calories_burned']} kcal")
            st.write("")


def display_training_calendar(calendar_events):
    """Displays the interactive training calendar widget."""
    st.subheader("Training Calendar")

    calendar_options = {
        "headerToolbar": {
            "left": "today prev,next",
            "center": "title",
            "right": "dayGridMonth,timeGridWeek,listWeek",
        },
        "initialView": "dayGridMonth",
        "navLinks": True, 
        "eventBorderRadius": "6px", 
        "themeSystem": "standard",
        "height": 600, 
    }

    calendar(events=calendar_events, options=calendar_options)


def display_share_progress(user_id, user_workouts):
    """Displays the UI for calculating totals and sharing them to the community feed."""
    st.subheader("Share your progress!")

    total_steps    = sum(w.get('steps', 0) or 0 for w in user_workouts)
    total_calories = sum(w.get('calories_burned', 0) or 0 for w in user_workouts)
    total_distance = sum(w.get('distance', 0) or 0 for w in user_workouts)

    stat_choice = st.selectbox(
        "Choose a stat to share:",
        ["Steps", "Calories Burned", "Distance"]
    )

    if stat_choice == "Steps":
        default_msg = f"I just hit {total_steps:,} total steps! Who wants to join me for my next workout?"
    elif stat_choice == "Calories Burned":
        default_msg = f"I just burned {total_calories:.0f} calories! Feeling great 🔥"
    else:
        default_msg = f"I just covered {total_distance:.1f} km! Let's get moving 📍"

    custom_msg = st.text_area("Customize your message:", value=default_msg)
    st.info(f"**Preview:** {custom_msg}")

    if st.button("🚀 Share to Community Feed"):
        try:
            create_shared_post(user_id, custom_msg)
            update_streak(user_id)
            st.success("Successfully posted to the Community Feed!")
            st.balloons()
        except Exception as e:
            st.error(f"Failed to post: {e}")


# =====================================================================
# 6. PROFILE PAGE UI
# =====================================================================

def display_profile_header(full_name, username, profile_image, friends_count):
    """Displays the user's profile picture, name, and basic info."""
    if profile_image:
        st.image(profile_image, width=150)
    
    st.subheader(full_name)
    st.write(f"@{username} | {friends_count} friends")


def display_streak_details(current_streak):
    """Displays the detailed streak metric and conditional motivational messages."""
    st.subheader("🔥 Workout Streak")

    if current_streak > 0:
        st.metric(label="Current Streak", value=f"{current_streak} 🔥")
    else:
        st.metric(label="Current Streak", value="0 😴")

    if current_streak == 0:
        st.info("No active streak. Log a workout to start one!")
    elif current_streak >= 7:
        st.success(f"You're on a {current_streak}-day streak! Incredible consistency 🏆")
    elif current_streak >= 3:
        st.success(f"You're on a {current_streak}-day streak! Keep it going 💪")
    else:
        st.success(f"You're on a {current_streak}-day streak! Great start 🔥")


# =====================================================================
# 7. COMMUNITY FEED UI
# =====================================================================

def display_genai_advice(timestamp, content, image):
    """Displays a motivational advice snippet generated by GenAI."""
    st.subheader("GenAI Advice")
    with st.container(border=True):
        st.caption(timestamp)
        st.write(content)
    if image:
        st.image(image, use_column_width=True) 


def display_post(username, user_image, timestamp, content, post_image):
    """Displays a single formatted social media post card."""
    with st.container(border=True):
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
                st.markdown(f"<div style='text-align:right'>{timestamp}</div>", unsafe_allow_html=True)

        st.divider()

        if content and content != "None":
            st.write(content)
        else:
            st.caption("_(no caption)_")

        if post_image and post_image != "None":
            try:
                st.image(post_image, use_column_width=True)
            except Exception:
                pass

        # Interactive footer (likes, comments, save)
        like_col, comment_col, spacer, save_col = st.columns([1, 1, 6, 1])
        with like_col:
            st.markdown("⭐ 0")
        with comment_col:
            st.markdown("💬 0")
        with save_col:
            st.markdown("<div style='text-align:right'>🔖</div>", unsafe_allow_html=True)
    st.write("")


def display_community_feed(posts):
    """Loops through and renders an entire list of community posts."""
    if not posts:
        st.info("Your friends haven't posted anything yet! Check back later.")
    else:
        for post in posts:
            display_post(
                username=post['username'],
                user_image=post['user_image'],
                timestamp=str(post['timestamp']),
                content=post['content'],
                post_image=post['post_image']
            )


# =====================================================================
# 8. AI COACH UI
# =====================================================================

def display_ai_suggestions_tabs(user_id, suggestions):
    """Renders AI workout suggestions using an interactive tabbed interface."""
    st.subheader("Your Custom Suggestions")
    
    # Extract titles and create tabs
    tab_names = [suggestion['workout_type'] for suggestion in suggestions]
    tabs = st.tabs(tab_names)
    
    # Populate each tab with specific suggestion details
    for i, suggestion in enumerate(suggestions):
        with tabs[i]:
            st.markdown(f"### 🏅 {suggestion['title']}")
            st.caption(f"**⏱️ Total Time:** {suggestion['total_time']} mins")
            st.info(suggestion['description'])
            
            # Scheduling controls
            col1, col2 = st.columns([2, 1])
            with col1:
                future_date = st.date_input(
                    "Schedule for:", 
                    value=datetime.date.today() + datetime.timedelta(days=1),
                    min_value=datetime.date.today(),
                    key=f"date_{i}"
                )
            with col2:
                st.write("") 
                st.write("")
                if st.button("Add to Calendar", key=f"add_{i}", use_container_width=True, type="primary"):
                    schedule_ai_workout(user_id, suggestion['workout_type'], future_date, suggestion['total_time'])
                    st.success(f"Added to {suggestion['workout_type']} Calendar!")
                    st.rerun()


def display_scheduled_workouts(scheduled_workouts):
    """Renders the list of future workouts with a delete option."""
    st.subheader("🗓️ Your Scheduled AI Workouts")
    
    if not scheduled_workouts:
        st.info("You don't have any workouts scheduled for the future.")
    else:
        for workout in scheduled_workouts:
            with st.container(border=True):
                col1, col2, col3 = st.columns([3, 2, 1])
                with col1:
                    date_str = str(workout.StartTimestamp)[:10]
                    st.write(f"**{date_str}**")
                with col2:
                    st.write(f"{workout.WorkoutType} ({workout.TotalTimeMinutes} min)")
                with col3:
                    if st.button("🗑️ Delete", key=f"del_{workout.WorkoutId}"):
                        delete_workout(workout.WorkoutId)
                        st.rerun()