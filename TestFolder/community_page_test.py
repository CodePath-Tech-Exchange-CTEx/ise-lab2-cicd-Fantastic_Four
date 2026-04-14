import unittest
from unittest.mock import patch, MagicMock
import datetime
from view.community_page import show_community_page

# ---------------------------------------------------------------------------
# Data Factories (Centralized Mock Data Generation)
# ---------------------------------------------------------------------------
class DataFactory:
    """Helper class to generate consistent mock data for tests."""
    
    @staticmethod
    def genai_advice():
        return {
            'timestamp': '2024-07-29 12:00:00',
            'content': 'Keep pushing, you are doing great!',
            'image': 'http://example.com/advice.jpg'
        }

    @staticmethod
    def user_profile(friends=None):
        return {
            'full_name': 'Alice Johnson',
            'username': 'alicej',
            'date_of_birth': datetime.date(1990, 1, 15),
            'profile_image': 'http://example.com/alice.jpg',
            'friends': friends or []
        }

    @staticmethod
    def post(post_id, timestamp=None):
        return {
            'user_id': 'user2',
            'post_id': post_id,
            'username': 'bobsmith',
            'user_image': 'http://example.com/bob.jpg',
            'timestamp': timestamp or datetime.datetime(2024, 7, 29, 12, 0),
            'content': 'Great run today!',
            'post_image': None
        }

# ---------------------------------------------------------------------------
# Main Test Suite
# ---------------------------------------------------------------------------
class TestShowCommunityPage(unittest.TestCase):

    def setUp(self):
        """Initialize all patches and mocks before each test case."""
        self.patchers = [
            patch('view.community_page.st'),
            patch('view.community_page.display_post'),
            patch('view.community_page.display_genai_advice'),
            patch('view.community_page.get_user_posts'),
            patch('view.community_page.get_user_profile'),
            patch('view.community_page.get_genai_advice')
        ]
        
        # Start patchers and assign mocks to descriptive variable names
        (self.mock_st, self.mock_disp_post, self.mock_disp_advice, 
         self.mock_get_posts, self.mock_get_profile, self.mock_get_genai) = [p.start() for p in self.patchers]

        # Set default return values for standard happy-path scenarios
        self.mock_get_genai.return_value = DataFactory.genai_advice()
        self.mock_get_profile.return_value = DataFactory.user_profile()
        self.mock_get_posts.return_value = []

    def tearDown(self):
        """Stop all patchers to prevent side effects in other tests."""
        for p in self.patchers:
            p.stop()

    # --- UI & Structure Tests ---

    def test_basic_ui_elements(self):
        """Validate that core page elements like title and dividers are rendered."""
        show_community_page('user1')
        self.mock_st.title.assert_called_once_with("Community Feed 🌐")
        self.mock_st.divider.assert_called_once()
        self.mock_disp_advice.assert_called_once()

    # --- Business Logic Tests ---

    def test_fetches_posts_for_all_friends(self):
        """Ensure the app queries the database for every ID in the friend list."""
        friends = ['u2', 'u3', 'u4']
        self.mock_get_profile.return_value = DataFactory.user_profile(friends)
        
        show_community_page('user1')
        
        self.assertEqual(self.mock_get_posts.call_count, len(friends))
        for f_id in friends:
            self.mock_get_posts.assert_any_call(f_id)

    def test_sorting_and_truncation(self):
        """Validate that posts are sorted by date and limited to the top 10."""
        # Create 15 posts with unique, chronological timestamps
        posts = [DataFactory.post(f"p{i}", datetime.datetime(2024, 1, i+1)) for i in range(15)]
        self.mock_get_profile.return_value = DataFactory.user_profile(['friend1'])
        self.mock_get_posts.return_value = posts

        show_community_page('user1')

        # Verify truncation: display_post should only be called 10 times
        self.assertEqual(self.mock_disp_post.call_count, 10)
        
        # Verify sorting: the first post displayed should be the most recent (day 15)
        first_call_args = self.mock_disp_post.call_args_list[0]
        self.assertIn("2024-01-15", first_call_args[1]['timestamp'])

    def test_empty_feed_behavior(self):
        """Verify the info message is shown when friends have no recent activity."""
        self.mock_get_profile.return_value = DataFactory.user_profile(['friend1'])
        self.mock_get_posts.return_value = []

        show_community_page('user1')

        self.mock_st.info.assert_called_once_with(
            "Your friends haven't posted anything yet! Check back later."
        )
        # Ensure that no posts were actually rendered
        self.mock_disp_post.assert_not_called()
if __name__ == "__main__":
    unittest.main()