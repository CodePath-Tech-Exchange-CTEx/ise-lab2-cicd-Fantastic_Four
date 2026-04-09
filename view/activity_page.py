import streamlit as st

# Import our backend functions
from data_fetcher import get_user_workouts, create_shared_post, update_streak

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

    # Calculate totals
    total_steps    = sum(w.get('steps', 0) or 0 for w in user_workouts)
    total_calories = sum(w.get('calories_burned', 0) or 0 for w in user_workouts)
    total_distance = sum(w.get('distance', 0) or 0 for w in user_workouts)

    # Let the user pick which stat to share
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

    # Let the user customize message
    custom_msg = st.text_area("Customize your message:", value=default_msg)

    # Show them a preview of what they are sharing
    st.info(f"**Preview:** {custom_msg}")

    # The actual button
    if st.button("🚀 Share to Community Feed"):
        try:
            create_shared_post(user_id, custom_msg)
            update_streak(user_id)
            st.success("Successfully posted to the Community Feed!")
            st.balloons()
        except Exception as e:
            st.error(f"Failed to post: {e}")
