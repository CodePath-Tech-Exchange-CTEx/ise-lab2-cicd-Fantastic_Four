import streamlit as st
import datetime
from data_fetcher import generate_ai_workout_plan, schedule_ai_workout, get_scheduled_workouts, delete_workout

def show_ai_plan_page(user_id):
    st.title("🤖 AI Coach: Plan Your Week")
    st.write("Let your AI coach design your next session. Pick a suggestion and add it to your calendar.")
    
    # Generate Suggestions Section
    if st.button("Generate New Workout Ideas", type="primary"):
        with st.spinner("Coach is thinking..."):
            st.session_state['ai_suggestions'] = generate_ai_workout_plan(user_id)
            
    # Display the suggestions if they exist in the session state
    # Display the suggestions if they exist in the session state
    if 'ai_suggestions' in st.session_state and st.session_state['ai_suggestions']:
        st.divider()
        st.subheader("Your Custom Suggestions")
        
        # 1. Extract the workout types to use as tab names
        tab_names = [suggestion['workout_type'] for suggestion in st.session_state['ai_suggestions']]
        
        # 2. Create the tabs
        tabs = st.tabs(tab_names)
        
        # 3. Populate each tab
        for i, suggestion in enumerate(st.session_state['ai_suggestions']):
            with tabs[i]:
                st.markdown(f"### 🏅 {suggestion['title']}")
                st.caption(f"**⏱️ Total Time:** {suggestion['total_time']} mins")
                
                # Using an info box makes the description pop
                st.info(suggestion['description'])
                
                # Put the date picker and button side-by-side for a cleaner look
                col1, col2 = st.columns([2, 1])
                with col1:
                    future_date = st.date_input(
                        "Schedule for:", 
                        value=datetime.date.today() + datetime.timedelta(days=1),
                        min_value=datetime.date.today(),
                        key=f"date_{i}"
                    )
                with col2:
                    st.write("") # A little spacer to push the button down so it aligns
                    st.write("")
                    if st.button("Add to Calendar", key=f"add_{i}", use_container_width=True, type="primary"):
                        schedule_ai_workout(user_id, suggestion['workout_type'], future_date, suggestion['total_time'])
                        st.success(f"Added to {suggestion['workout_type']} Calendar!")
                        st.rerun()
    st.divider()
    
    # 2. Manage Scheduled Workouts Section
    st.subheader("🗓️ Your Scheduled AI Workouts")
    scheduled = get_scheduled_workouts(user_id)
    
    if not scheduled:
        st.info("You don't have any workouts scheduled for the future.")
    else:
        for workout in scheduled:
            with st.container(border=True):
                col1, col2, col3 = st.columns([3, 2, 1])
                with col1:
                    # Clean up the timestamp for display
                    date_str = str(workout.StartTimestamp)[:10]
                    st.write(f"**{date_str}**")
                with col2:
                    st.write(f"{workout.WorkoutType} ({workout.TotalTimeMinutes} min)")
                with col3:
                    if st.button("🗑️ Delete", key=f"del_{workout.WorkoutId}"):
                        delete_workout(workout.WorkoutId)
                        st.rerun()