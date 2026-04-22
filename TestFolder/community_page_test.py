#############################################################################
# community_page_test.py
#
# Unit tests for view/community_page.py
# All Streamlit and backend calls are mocked to run without dependencies.
#############################################################################

import unittest
from unittest.mock import patch, MagicMock, call
import datetime

from view.community_page import show_community_page


class TestCommunityPageDisplay(unittest.TestCase):
    """Tests for the show_community_page function."""

    @patch('view.community_page.display_community_feed')
    @patch('view.community_page.display_genai_advice')
    @patch('view.community_page.get_genai_advice')
    @patch('view.community_page.get_user_posts')
    @patch('view.community_page.get_user_profile')
    @patch('streamlit.divider')
    @patch('streamlit.subheader')
    @patch('streamlit.title')
    def test_show_community_page_displays_title(
        self, mock_title, mock_subheader, mock_divider,
        mock_get_profile, mock_get_posts, mock_get_advice,
        mock_display_advice, mock_display_feed
    ):
        """Test that the community page displays the correct title."""
        mock_get_advice.return_value = {
            'timestamp': '2026-04-21',
            'content': 'Great advice',
            'image': 'image.png'
        }
        mock_get_profile.return_value = {'friends': []}
        
        show_community_page('user1')
        
        mock_title.assert_called_once_with("Community Feed 🌐")

    @patch('view.community_page.display_community_feed')
    @patch('view.community_page.display_genai_advice')
    @patch('view.community_page.get_genai_advice')
    @patch('view.community_page.get_user_posts')
    @patch('view.community_page.get_user_profile')
    @patch('streamlit.divider')
    @patch('streamlit.subheader')
    @patch('streamlit.title')
    def test_show_community_page_fetches_genai_advice(
        self, mock_title, mock_subheader, mock_divider,
        mock_get_profile, mock_get_posts, mock_get_advice,
        mock_display_advice, mock_display_feed
    ):
        """Test that GenAI advice is fetched and displayed."""
        advice_data = {
            'timestamp': '2026-04-21 10:00:00',
            'content': 'Keep up the great work!',
            'image': 'advice.png'
        }
        mock_get_advice.return_value = advice_data
        mock_get_profile.return_value = {'friends': []}
        
        show_community_page('user1')
        
        mock_get_advice.assert_called_once_with('user1')
        mock_display_advice.assert_called_once_with(
            advice_data['timestamp'],
            advice_data['content'],
            advice_data['image']
        )

    @patch('view.community_page.display_community_feed')
    @patch('view.community_page.display_genai_advice')
    @patch('view.community_page.get_genai_advice')
    @patch('view.community_page.get_user_posts')
    @patch('view.community_page.get_user_profile')
    @patch('streamlit.divider')
    @patch('streamlit.subheader')
    @patch('streamlit.title')
    def test_show_community_page_fetches_friends_posts(
        self, mock_title, mock_subheader, mock_divider,
        mock_get_profile, mock_get_posts, mock_get_advice,
        mock_display_advice, mock_display_feed
    ):
        """Test that friends' posts are fetched from all friends."""
        mock_get_advice.return_value = {
            'timestamp': '2026-04-21',
            'content': 'Advice',
            'image': 'image.png'
        }
        mock_get_profile.return_value = {'friends': ['friend1', 'friend2', 'friend3']}
        
        friend1_posts = [{'timestamp': '2026-04-21 08:00', 'content': 'Post from friend1'}]
        friend2_posts = [{'timestamp': '2026-04-20 10:00', 'content': 'Post from friend2'}]
        friend3_posts = []
        
        mock_get_posts.side_effect = [friend1_posts, friend2_posts, friend3_posts]
        
        show_community_page('user1')
        
        self.assertEqual(mock_get_posts.call_count, 3)
        mock_get_posts.assert_any_call('friend1')
        mock_get_posts.assert_any_call('friend2')
        mock_get_posts.assert_any_call('friend3')

    @patch('view.community_page.display_community_feed')
    @patch('view.community_page.display_genai_advice')
    @patch('view.community_page.get_genai_advice')
    @patch('view.community_page.get_user_posts')
    @patch('view.community_page.get_user_profile')
    @patch('streamlit.divider')
    @patch('streamlit.subheader')
    @patch('streamlit.title')
    def test_show_community_page_sorts_posts_by_timestamp(
        self, mock_title, mock_subheader, mock_divider,
        mock_get_profile, mock_get_posts, mock_get_advice,
        mock_display_advice, mock_display_feed
    ):
        """Test that posts are sorted by timestamp (newest first)."""
        mock_get_advice.return_value = {
            'timestamp': '2026-04-21',
            'content': 'Advice',
            'image': 'image.png'
        }
        mock_get_profile.return_value = {'friends': ['friend1', 'friend2']}
        
        # Create posts with different timestamps
        posts_from_friend1 = [
            {'timestamp': '2026-04-19 10:00', 'content': 'Old post'},
            {'timestamp': '2026-04-21 12:00', 'content': 'Newest post'}
        ]
        posts_from_friend2 = [
            {'timestamp': '2026-04-20 15:00', 'content': 'Middle post'}
        ]
        
        mock_get_posts.side_effect = [posts_from_friend1, posts_from_friend2]
        
        show_community_page('user1')
        
        # Verify that display_community_feed was called
        mock_display_feed.assert_called_once()
        
        # Get the posts that were passed to display_community_feed
        passed_posts = mock_display_feed.call_args[0][0]
        
        # Verify posts are sorted correctly (newest first) and limited to 10
        self.assertEqual(len(passed_posts), 3)
        self.assertEqual(passed_posts[0]['timestamp'], '2026-04-21 12:00')
        self.assertEqual(passed_posts[1]['timestamp'], '2026-04-20 15:00')
        self.assertEqual(passed_posts[2]['timestamp'], '2026-04-19 10:00')

    @patch('view.community_page.display_community_feed')
    @patch('view.community_page.display_genai_advice')
    @patch('view.community_page.get_genai_advice')
    @patch('view.community_page.get_user_posts')
    @patch('view.community_page.get_user_profile')
    @patch('streamlit.divider')
    @patch('streamlit.subheader')
    @patch('streamlit.title')
    def test_show_community_page_limits_to_top_10_posts(
        self, mock_title, mock_subheader, mock_divider,
        mock_get_profile, mock_get_posts, mock_get_advice,
        mock_display_advice, mock_display_feed
    ):
        """Test that only top 10 posts are displayed."""
        mock_get_advice.return_value = {
            'timestamp': '2026-04-21',
            'content': 'Advice',
            'image': 'image.png'
        }
        mock_get_profile.return_value = {'friends': ['friend1']}
        
        # Create 15 posts
        posts = [{'timestamp': f'2026-04-21 {i:02d}:00', 'content': f'Post {i}'} for i in range(15)]
        mock_get_posts.return_value = posts
        
        show_community_page('user1')
        
        # Verify that only top 10 are passed to display
        passed_posts = mock_display_feed.call_args[0][0]
        self.assertEqual(len(passed_posts), 10)

    @patch('view.community_page.display_community_feed')
    @patch('view.community_page.display_genai_advice')
    @patch('view.community_page.get_genai_advice')
    @patch('view.community_page.get_user_posts')
    @patch('view.community_page.get_user_profile')
    @patch('streamlit.divider')
    @patch('streamlit.subheader')
    @patch('streamlit.title')
    def test_show_community_page_handles_no_friends(
        self, mock_title, mock_subheader, mock_divider,
        mock_get_profile, mock_get_posts, mock_get_advice,
        mock_display_advice, mock_display_feed
    ):
        """Test that the page handles users with no friends."""
        mock_get_advice.return_value = {
            'timestamp': '2026-04-21',
            'content': 'Advice',
            'image': 'image.png'
        }
        mock_get_profile.return_value = {'friends': []}
        
        show_community_page('user1')
        
        mock_get_posts.assert_not_called()
        # Display feed should still be called with empty list
        mock_display_feed.assert_called_once_with([])

    @patch('view.community_page.display_community_feed')
    @patch('view.community_page.display_genai_advice')
    @patch('view.community_page.get_genai_advice')
    @patch('view.community_page.get_user_posts')
    @patch('view.community_page.get_user_profile')
    @patch('streamlit.divider')
    @patch('streamlit.subheader')
    @patch('streamlit.title')
    def test_show_community_page_calls_dividers(
        self, mock_title, mock_subheader, mock_divider,
        mock_get_profile, mock_get_posts, mock_get_advice,
        mock_display_advice, mock_display_feed
    ):
        """Test that dividers are displayed between sections."""
        mock_get_advice.return_value = {
            'timestamp': '2026-04-21',
            'content': 'Advice',
            'image': 'image.png'
        }
        mock_get_profile.return_value = {'friends': []}
        
        show_community_page('user1')
        
        # Should call divider once (after advice)
        self.assertEqual(mock_divider.call_count, 1)


if __name__ == '__main__':
    unittest.main()
