import streamlit as st

# Import our backend functions
from data_fetcher import get_user_workouts, create_shared_post

# Import the UI components
from modules import display_activity_summary, display_recent_workouts

def show_activity_page(user_id):
    st.title("My Activity Dashboard 🏃‍♂️")
    
    # 1. Fetch the user's workouts
    user_workouts = get_user_workouts(user_id)
    
    # 2. Display the UI components
    display_activity_summary(user_workouts)
    display_recent_workouts(user_workouts)
    
    st.divider()
    
    # ==========================================
    # 3. The "Share" Button Feature
    # ==========================================
    st.subheader("Share your progress!")
    
    # Let's calculate their total steps to share
    total_steps = 0
    for workout in user_workouts:
        total_steps += workout['steps']
        
    post_text = f"I just hit {total_steps} total steps! Who wants to join me for my next workout?"
    
    # Show them a preview of what they are sharing
    st.info(f"**Preview:** {post_text}")
    
    # The actual button
    if st.button("🚀 Share to Community Feed"):
        # This calls the BigQuery INSERT function we just wrote!
        create_shared_post(user_id, post_text)
        
        st.success("Successfully posted to the Community Feed!")
        st.balloons() # A little celebration animation!