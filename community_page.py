import streamlit as st

# Import the backend functions you wrote
from data_fetcher import get_user_profile, get_user_posts, get_genai_advice

# Import the UI components from modules.py
from modules import display_post, display_genai_advice

def show_community_page(user_id):
    st.title("Community Feed 🌐")
    
    # ==========================================
    # 1. Display GenAI Advice
    # ==========================================
    # We fetch the dictionary and pass its pieces to the display module
    genai_data = get_genai_advice(user_id)
    display_genai_advice(genai_data['timestamp'], genai_data['content'], genai_data['image'])
    
    st.divider()
    
    # ==========================================
    # 2. Gather and Display Friends' Posts
    # ==========================================
    st.subheader("What your friends are up to")
    
    # Step A: Get the user's profile to find out who their friends are
    user_profile = get_user_profile(user_id)
    friends_list = user_profile.get('friends', [])
    
    all_friends_posts = []
    
    # Step B: Loop through every friend and grab their posts
    for friend_id in friends_list:
        friend_posts = get_user_posts(friend_id)
        all_friends_posts.extend(friend_posts) # Add this friend's posts to our giant list
        
    # Step C: Sort the giant list by timestamp (newest first)
    # The lambda function tells Python to look at the 'timestamp' key in the dictionary to sort
    sorted_posts = sorted(all_friends_posts, key=lambda x: x['timestamp'], reverse=True)
    
    # Step D: Keep only the top 10 most recent posts
    top_10_posts = sorted_posts[:10]
    
    # Step E: Display them!
    if not top_10_posts:
        st.info("Your friends haven't posted anything yet! Check back later.")
    else:
        for post in top_10_posts:
            display_post(
                username=post['username'],
                user_image=post['user_image'],
                timestamp=str(post['timestamp']), # Ensure it's a string for Streamlit
                content=post['content'],
                post_image=post['post_image']
            )