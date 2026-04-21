import streamlit as st

# Import backend fetching/generating logic
from data_fetcher import generate_ai_workout_plan, get_scheduled_workouts

# Import our new UI components from modules.py
from modules import display_ai_suggestions_tabs, display_scheduled_workouts

def show_ai_plan_page(user_id):
    st.title("🤖 AI Coach: Plan Your Week")
    st.write("Let your AI coach design your next session. Pick a suggestion and add it to your calendar.")
    
    # 1. Controller Logic: Generate Suggestions
    if st.button("Generate New Workout Ideas", type="primary"):
        with st.spinner("Coach is thinking..."):
            st.session_state['ai_suggestions'] = generate_ai_workout_plan(user_id)
            
    # 2. View Logic: Display Suggestions via Tabs
    if 'ai_suggestions' in st.session_state and st.session_state['ai_suggestions']:
        st.divider()
        display_ai_suggestions_tabs(user_id, st.session_state['ai_suggestions'])

    st.divider()
    
    # 3. Controller Logic: Fetch Scheduled Data
    scheduled = get_scheduled_workouts(user_id)
    
    # 4. View Logic: Display Scheduled Workouts
    display_scheduled_workouts(scheduled)

