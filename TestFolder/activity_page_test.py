import unittest
from unittest.mock import patch, MagicMock
from view.activity_page import show_activity_page

# ---------------------------------------------------------------------------
# Data Factories
# ---------------------------------------------------------------------------
class DataFactory:
    @staticmethod
    def workouts():
        """Returns a sample list of workout dictionaries."""
        return [
            {'steps': 5000, 'calories_burned': 300, 'distance': 3.5},
            {'steps': 2000, 'calories_burned': 150, 'distance': 1.5},
            {'steps': None, 'calories_burned': 50,  'distance': 0.5} # Testing None handling
        ]

# ---------------------------------------------------------------------------
# Main Test Suite
# ---------------------------------------------------------------------------
class TestShowActivityPage(unittest.TestCase):

    def setUp(self):
        """Initialize mocks for Streamlit, modules, and data fetchers."""
        self.patchers = [
            patch('view.activity_page.st'),
            patch('view.activity_page.get_user_workouts'),
            patch('view.activity_page.create_shared_post'),
            patch('view.activity_page.update_streak'),
            patch('view.activity_page.display_activity_summary'),
            patch('view.activity_page.display_recent_workouts')
        ]
        
        (self.mock_st, self.mock_get_workouts, self.mock_create_post, 
         self.mock_update_streak, self.mock_disp_summary, self.mock_disp_recent) = [p.start() for p in self.patchers]

        # Default: user has some workouts
        self.mock_get_workouts.return_value = DataFactory.workouts()

    def tearDown(self):
        """Clean up patches."""
        for p in self.patchers:
            p.stop()

    def test_page_renders_initial_components(self):
        """Ensure title and summary components are called correctly."""
        show_activity_page('user123')
        
        self.mock_st.title.assert_called_once_with("My Activity Dashboard 🏃‍♂️")
        self.mock_get_workouts.assert_called_once_with('user123')
        self.mock_disp_summary.assert_called_once()
        self.mock_disp_recent.assert_called_once()

    def test_stat_selection_logic_steps(self):
        """Verify the default message generated for 'Steps' selection."""
        # Mock the selectbox to return 'Steps'
        self.mock_st.selectbox.return_value = "Steps"
        self.mock_st.text_area.return_value = "I just hit 7,000 total steps!"
        
        show_activity_page('user123')
        
        # Check if text_area was initialized with the correct formatted steps string
        # total_steps from DataFactory is 7000
        args, kwargs = self.mock_st.text_area.call_args
        self.assertIn("7,000 total steps", kwargs['value'])

    def test_share_button_success(self):
        """Verify backend calls and UI feedback on successful post."""
        self.mock_st.selectbox.return_value = "Distance"
        self.mock_st.text_area.return_value = "Custom message"
        self.mock_st.button.return_value = True # Simulate button click
        
        show_activity_page('user_99')
        
        # Verify both backend functions were triggered
        self.mock_create_post.assert_called_once_with('user_99', "Custom message")
        self.mock_update_streak.assert_called_once_with('user_99')
        
        # Verify UI celebration
        self.mock_st.success.assert_called_once()
        self.mock_st.balloons.assert_called_once()

    def test_share_button_failure(self):
        """Ensure error handling if the database/API call fails."""
        self.mock_st.button.return_value = True
        self.mock_create_post.side_effect = Exception("Database Timeout")
        
        show_activity_page('user_99')
        
        # Verify error message was shown
        self.mock_st.error.assert_called_once()
        self.assertIn("Database Timeout", self.mock_st.error.call_args[0][0])
        # Streak should not update if post fails (depending on your logic)
        self.mock_update_streak.assert_not_called()

if __name__ == '__main__':
    unittest.main()