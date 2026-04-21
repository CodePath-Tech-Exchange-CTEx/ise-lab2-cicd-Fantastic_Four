import streamlit as st

# Import the backend functions 
from data_fetcher import get_user_profile, get_user_posts, get_genai_advice

# Import the UI components from modules.py
from modules import display_genai_advice, display_community_feed

def show_community_page(user_id):
    st.title("Community Feed 🌐")
    
    # ==========================================
    # 1. Fetch & Display GenAI Advice
    # ==========================================
    genai_data = get_genai_advice(user_id)
    display_genai_advice(genai_data['timestamp'], genai_data['content'], genai_data['image'])
    
    st.divider()
    
    # ==========================================
    # 2. Controller: Gather Friends' Posts
    # ==========================================
    st.subheader("What your friends are up to")
    
    user_profile = get_user_profile(user_id)
    friends_list = user_profile.get('friends', [])
    
    all_friends_posts = []
    
    # Loop through every friend and grab their posts
    for friend_id in friends_list:
        friend_posts = get_user_posts(friend_id)
        all_friends_posts.extend(friend_posts)
        
    # Sort the giant list by timestamp (newest first) and grab top 10
    sorted_posts = sorted(all_friends_posts, key=lambda x: x['timestamp'], reverse=True)
    top_10_posts = sorted_posts[:10]
    
    # ==========================================
    # 3. View: Display the Feed
    # ==========================================
    display_community_feed(top_10_posts)