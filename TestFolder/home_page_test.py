#############################################################################
# home_page_test.py
#
# Unit tests for view/home_page.py
# All Streamlit and backend calls are mocked to run without dependencies.
#############################################################################

import unittest
from unittest.mock import patch, MagicMock

from view.home_page import home_page


class TestHomePage(unittest.TestCase):
    """Tests for the home_page function."""

    @patch('view.home_page.display_dynamic_workout_form')
    @patch('view.home_page.display_activity_grid')
    @patch('view.home_page.display_streak_badge')
    @patch('view.home_page.get_streak')
    @patch('view.home_page.get_user_profile')
    @patch('streamlit.write')
    @patch('streamlit.title')
    @patch('streamlit.divider')
    def test_home_page_initializes_session_state(
        self, mock_divider, mock_title, mock_write,
        mock_get_profile, mock_get_streak, mock_display_badge, mock_display_grid, mock_display_form
    ):
        """Test that session state is initialized for selected_workout_type."""
        mock_get_profile.return_value = {'full_name': 'John Doe'}
        mock_get_streak.return_value = {'current_streak': 5}
        
        with patch.dict('streamlit.session_state', {}, clear=True) as session_state:
            home_page('user1')
            
            self.assertIn('selected_workout_type', session_state)
            self.assertIsNone(session_state['selected_workout_type'])

    @patch('view.home_page.display_dynamic_workout_form')
    @patch('view.home_page.display_activity_grid')
    @patch('view.home_page.display_streak_badge')
    @patch('view.home_page.get_streak')
    @patch('view.home_page.get_user_profile')
    @patch('streamlit.write')
    @patch('streamlit.title')
    @patch('streamlit.divider')
    def test_home_page_fetches_user_profile(
        self, mock_divider, mock_title, mock_write,
        mock_get_profile, mock_get_streak, mock_display_badge, mock_display_grid, mock_display_form
    ):
        """Test that user profile is fetched."""
        mock_get_profile.return_value = {'full_name': 'Jane Doe'}
        mock_get_streak.return_value = {'current_streak': 3}
        
        with patch.dict('streamlit.session_state', {}, clear=True):
            home_page('user1')
        
        mock_get_profile.assert_called_once_with('user1')

    @patch('view.home_page.display_dynamic_workout_form')
    @patch('view.home_page.display_activity_grid')
    @patch('view.home_page.display_streak_badge')
    @patch('view.home_page.get_streak')
    @patch('view.home_page.get_user_profile')
    @patch('streamlit.write')
    @patch('streamlit.title')
    @patch('streamlit.divider')
    def test_home_page_fetches_streak_data(
        self, mock_divider, mock_title, mock_write,
        mock_get_profile, mock_get_streak, mock_display_badge, mock_display_grid, mock_display_form
    ):
        """Test that streak data is fetched."""
        mock_get_profile.return_value = {'full_name': 'John Doe'}
        mock_get_streak.return_value = {'current_streak': 7}
        
        with patch.dict('streamlit.session_state', {}, clear=True):
            home_page('user1')
        
        mock_get_streak.assert_called_once_with('user1')

    @patch('view.home_page.display_dynamic_workout_form')
    @patch('view.home_page.display_activity_grid')
    @patch('view.home_page.display_streak_badge')
    @patch('view.home_page.get_streak')
    @patch('view.home_page.get_user_profile')
    @patch('streamlit.write')
    @patch('streamlit.title')
    @patch('streamlit.divider')
    def test_home_page_displays_streak_badge(
        self, mock_divider, mock_title, mock_write,
        mock_get_profile, mock_get_streak, mock_display_badge, mock_display_grid, mock_display_form
    ):
        """Test that streak badge is displayed with streak count."""
        mock_get_profile.return_value = {'full_name': 'John Doe'}
        mock_get_streak.return_value = {'current_streak': 10}
        
        with patch.dict('streamlit.session_state', {}, clear=True):
            home_page('user1')
        
        mock_display_badge.assert_called_once_with(10)

    @patch('view.home_page.display_dynamic_workout_form')
    @patch('view.home_page.display_activity_grid')
    @patch('view.home_page.display_streak_badge')
    @patch('view.home_page.get_streak')
    @patch('view.home_page.get_user_profile')
    @patch('streamlit.write')
    @patch('streamlit.title')
    @patch('streamlit.divider')
    def test_home_page_displays_personalized_greeting(
        self, mock_divider, mock_title, mock_write,
        mock_get_profile, mock_get_streak, mock_display_badge, mock_display_grid, mock_display_form
    ):
        """Test that page displays greeting with user's name."""
        mock_get_profile.return_value = {'full_name': 'Alice Smith'}
        mock_get_streak.return_value = {'current_streak': 2}
        
        with patch.dict('streamlit.session_state', {}, clear=True):
            home_page('user1')
        
        mock_title.assert_called_once_with("Hello Alice Smith 👋")

    @patch('view.home_page.display_dynamic_workout_form')
    @patch('view.home_page.display_activity_grid')
    @patch('view.home_page.display_streak_badge')
    @patch('view.home_page.get_streak')
    @patch('view.home_page.get_user_profile')
    @patch('streamlit.write')
    @patch('streamlit.title')
    @patch('streamlit.divider')
    def test_home_page_displays_reminder_message(
        self, mock_divider, mock_title, mock_write,
        mock_get_profile, mock_get_streak, mock_display_badge, mock_display_grid, mock_display_form
    ):
        """Test that reminder message is displayed."""
        mock_get_profile.return_value = {'full_name': 'John Doe'}
        mock_get_streak.return_value = {'current_streak': 0}
        
        with patch.dict('streamlit.session_state', {}, clear=True):
            home_page('user1')
        
        # Verify write was called for reminder message
        write_calls = [call[0][0] for call in mock_write.call_args_list]
        self.assertIn("Don't forget to log a physical activity today", write_calls)

    @patch('view.home_page.display_dynamic_workout_form')
    @patch('view.home_page.display_activity_grid')
    @patch('view.home_page.display_streak_badge')
    @patch('view.home_page.get_streak')
    @patch('view.home_page.get_user_profile')
    @patch('streamlit.write')
    @patch('streamlit.title')
    @patch('streamlit.divider')
    def test_home_page_displays_activity_grid(
        self, mock_divider, mock_title, mock_write,
        mock_get_profile, mock_get_streak, mock_display_badge, mock_display_grid, mock_display_form
    ):
        """Test that activity grid is displayed."""
        mock_get_profile.return_value = {'full_name': 'John Doe'}
        mock_get_streak.return_value = {'current_streak': 5}
        
        with patch.dict('streamlit.session_state', {}, clear=True):
            home_page('user1')
        
        mock_display_grid.assert_called_once()

    @patch('view.home_page.display_dynamic_workout_form')
    @patch('view.home_page.display_activity_grid')
    @patch('view.home_page.display_streak_badge')
    @patch('view.home_page.get_streak')
    @patch('view.home_page.get_user_profile')
    @patch('streamlit.write')
    @patch('streamlit.title')
    @patch('streamlit.divider')
    def test_home_page_does_not_display_form_when_no_workout_selected(
        self, mock_divider, mock_title, mock_write,
        mock_get_profile, mock_get_streak, mock_display_badge, mock_display_grid, mock_display_form
    ):
        """Test that workout form is not displayed when no workout type is selected."""
        mock_get_profile.return_value = {'full_name': 'John Doe'}
        mock_get_streak.return_value = {'current_streak': 5}
        
        with patch.dict('streamlit.session_state', {'selected_workout_type': None}, clear=True):
            home_page('user1')
        
        mock_display_form.assert_not_called()

    @patch('view.home_page.display_dynamic_workout_form')
    @patch('view.home_page.display_activity_grid')
    @patch('view.home_page.display_streak_badge')
    @patch('view.home_page.get_streak')
    @patch('view.home_page.get_user_profile')
    @patch('streamlit.write')
    @patch('streamlit.title')
    @patch('streamlit.divider')
    def test_home_page_displays_form_when_workout_selected(
        self, mock_divider, mock_title, mock_write,
        mock_get_profile, mock_get_streak, mock_display_badge, mock_display_grid, mock_display_form
    ):
        """Test that workout form is displayed when a workout type is selected."""
        mock_get_profile.return_value = {'full_name': 'John Doe'}
        mock_get_streak.return_value = {'current_streak': 5}
        
        with patch.dict('streamlit.session_state', {'selected_workout_type': 'Running'}, clear=True):
            home_page('user1')
        
        mock_display_form.assert_called_once_with('user1', 'Running')

    @patch('view.home_page.display_dynamic_workout_form')
    @patch('view.home_page.display_activity_grid')
    @patch('view.home_page.display_streak_badge')
    @patch('view.home_page.get_streak')
    @patch('view.home_page.get_user_profile')
    @patch('streamlit.write')
    @patch('streamlit.title')
    @patch('streamlit.divider')
    def test_home_page_passes_correct_user_id_to_form(
        self, mock_divider, mock_title, mock_write,
        mock_get_profile, mock_get_streak, mock_display_badge, mock_display_grid, mock_display_form
    ):
        """Test that correct user ID is passed to workout form."""
        mock_get_profile.return_value = {'full_name': 'John Doe'}
        mock_get_streak.return_value = {'current_streak': 5}
        
        with patch.dict('streamlit.session_state', {'selected_workout_type': 'Cycling'}, clear=True):
            home_page('user123')
        
        mock_display_form.assert_called_once()
        call_args = mock_display_form.call_args[0]
        self.assertEqual(call_args[0], 'user123')

    @patch('view.home_page.display_dynamic_workout_form')
    @patch('view.home_page.display_activity_grid')
    @patch('view.home_page.display_streak_badge')
    @patch('view.home_page.get_streak')
    @patch('view.home_page.get_user_profile')
    @patch('streamlit.write')
    @patch('streamlit.title')
    @patch('streamlit.divider')
    def test_home_page_handles_missing_full_name(
        self, mock_divider, mock_title, mock_write,
        mock_get_profile, mock_get_streak, mock_display_badge, mock_display_grid, mock_display_form
    ):
        """Test that page handles missing full_name gracefully."""
        mock_get_profile.return_value = {}
        mock_get_streak.return_value = {'current_streak': 0}
        
        with patch.dict('streamlit.session_state', {}, clear=True):
            home_page('user1')
        
        mock_title.assert_called_once_with("Hello User 👋")

    @patch('view.home_page.display_dynamic_workout_form')
    @patch('view.home_page.display_activity_grid')
    @patch('view.home_page.display_streak_badge')
    @patch('view.home_page.get_streak')
    @patch('view.home_page.get_user_profile')
    @patch('streamlit.write')
    @patch('streamlit.title')
    @patch('streamlit.divider')
    def test_home_page_handles_zero_streak(
        self, mock_divider, mock_title, mock_write,
        mock_get_profile, mock_get_streak, mock_display_badge, mock_display_grid, mock_display_form
    ):
        """Test that page handles zero streak correctly."""
        mock_get_profile.return_value = {'full_name': 'John Doe'}
        mock_get_streak.return_value = {'current_streak': 0}
        
        with patch.dict('streamlit.session_state', {}, clear=True):
            home_page('user1')
        
        mock_display_badge.assert_called_once_with(0)


if __name__ == '__main__':
    unittest.main()
