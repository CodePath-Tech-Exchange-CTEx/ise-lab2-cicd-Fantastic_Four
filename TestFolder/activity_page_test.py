#############################################################################
# activity_page_test.py
#
# Unit tests for view/activity_page.py
# All Streamlit and backend calls are mocked to run without dependencies.
#############################################################################

import unittest
from unittest.mock import patch, MagicMock
import datetime

from view.activity_page import show_activity_page


class TestActivityPageDisplay(unittest.TestCase):
    """Tests for the show_activity_page function."""

    def _make_sample_workouts(self):
        """Helper method to create sample workout data."""
        return [
            {
                'workout_id': 'w1',
                'type': 'Running',
                'calories_burned': 500,
                'distance': 5.0,
                'steps': 8000,
                'timestamp': '2026-04-21 08:00'
            },
            {
                'workout_id': 'w2',
                'type': 'Cycling',
                'calories_burned': 400,
                'distance': 20.0,
                'steps': 0,
                'timestamp': '2026-04-20 10:00'
            }
        ]

    @patch('view.activity_page.display_share_progress')
    @patch('view.activity_page.display_recent_workouts')
    @patch('view.activity_page.display_training_calendar')
    @patch('view.activity_page.display_activity_summary')
    @patch('view.activity_page.get_all_calendar_events')
    @patch('view.activity_page.get_user_workout_dates')
    @patch('view.activity_page.get_user_workouts')
    @patch('streamlit.divider')
    @patch('streamlit.title')
    def test_show_activity_page_displays_title(
        self, mock_title, mock_divider,
        mock_get_workouts, mock_get_dates, mock_get_events,
        mock_display_summary, mock_display_calendar, mock_display_recent, mock_display_share
    ):
        """Test that the activity page displays the correct title."""
        mock_get_workouts.return_value = self._make_sample_workouts()
        mock_get_dates.return_value = []
        mock_get_events.return_value = []
        
        show_activity_page('user1')
        
        mock_title.assert_called_once_with("My Activity Dashboard 🏃‍♂️")

    @patch('view.activity_page.display_share_progress')
    @patch('view.activity_page.display_recent_workouts')
    @patch('view.activity_page.display_training_calendar')
    @patch('view.activity_page.display_activity_summary')
    @patch('view.activity_page.get_all_calendar_events')
    @patch('view.activity_page.get_user_workout_dates')
    @patch('view.activity_page.get_user_workouts')
    @patch('streamlit.divider')
    @patch('streamlit.title')
    def test_show_activity_page_fetches_user_workouts(
        self, mock_title, mock_divider,
        mock_get_workouts, mock_get_dates, mock_get_events,
        mock_display_summary, mock_display_calendar, mock_display_recent, mock_display_share
    ):
        """Test that user workouts are fetched."""
        mock_get_workouts.return_value = self._make_sample_workouts()
        mock_get_dates.return_value = []
        mock_get_events.return_value = []
        
        show_activity_page('user1')
        
        mock_get_workouts.assert_called_once_with('user1')

    @patch('view.activity_page.display_share_progress')
    @patch('view.activity_page.display_recent_workouts')
    @patch('view.activity_page.display_training_calendar')
    @patch('view.activity_page.display_activity_summary')
    @patch('view.activity_page.get_all_calendar_events')
    @patch('view.activity_page.get_user_workout_dates')
    @patch('view.activity_page.get_user_workouts')
    @patch('streamlit.divider')
    @patch('streamlit.title')
    def test_show_activity_page_fetches_workout_dates(
        self, mock_title, mock_divider,
        mock_get_workouts, mock_get_dates, mock_get_events,
        mock_display_summary, mock_display_calendar, mock_display_recent, mock_display_share
    ):
        """Test that workout dates are fetched."""
        mock_get_workouts.return_value = self._make_sample_workouts()
        mock_get_dates.return_value = ['2026-04-21', '2026-04-20']
        mock_get_events.return_value = []
        
        show_activity_page('user1')
        
        mock_get_dates.assert_called_once_with('user1')

    @patch('view.activity_page.display_share_progress')
    @patch('view.activity_page.display_recent_workouts')
    @patch('view.activity_page.display_training_calendar')
    @patch('view.activity_page.display_activity_summary')
    @patch('view.activity_page.get_all_calendar_events')
    @patch('view.activity_page.get_user_workout_dates')
    @patch('view.activity_page.get_user_workouts')
    @patch('streamlit.divider')
    @patch('streamlit.title')
    def test_show_activity_page_fetches_calendar_events(
        self, mock_title, mock_divider,
        mock_get_workouts, mock_get_dates, mock_get_events,
        mock_display_summary, mock_display_calendar, mock_display_recent, mock_display_share
    ):
        """Test that calendar events are fetched."""
        mock_get_workouts.return_value = self._make_sample_workouts()
        mock_get_dates.return_value = []
        mock_get_events.return_value = [
            {'date': '2026-04-21', 'event': 'Race Day'},
            {'date': '2026-04-25', 'event': 'Training Session'}
        ]
        
        show_activity_page('user1')
        
        mock_get_events.assert_called_once_with('user1')

    @patch('view.activity_page.display_share_progress')
    @patch('view.activity_page.display_recent_workouts')
    @patch('view.activity_page.display_training_calendar')
    @patch('view.activity_page.display_activity_summary')
    @patch('view.activity_page.get_all_calendar_events')
    @patch('view.activity_page.get_user_workout_dates')
    @patch('view.activity_page.get_user_workouts')
    @patch('streamlit.divider')
    @patch('streamlit.title')
    def test_show_activity_page_displays_activity_summary(
        self, mock_title, mock_divider,
        mock_get_workouts, mock_get_dates, mock_get_events,
        mock_display_summary, mock_display_calendar, mock_display_recent, mock_display_share
    ):
        """Test that activity summary is displayed with workouts."""
        workouts = self._make_sample_workouts()
        mock_get_workouts.return_value = workouts
        mock_get_dates.return_value = []
        mock_get_events.return_value = []
        
        show_activity_page('user1')
        
        mock_display_summary.assert_called_once_with(workouts)

    @patch('view.activity_page.display_share_progress')
    @patch('view.activity_page.display_recent_workouts')
    @patch('view.activity_page.display_training_calendar')
    @patch('view.activity_page.display_activity_summary')
    @patch('view.activity_page.get_all_calendar_events')
    @patch('view.activity_page.get_user_workout_dates')
    @patch('view.activity_page.get_user_workouts')
    @patch('streamlit.divider')
    @patch('streamlit.title')
    def test_show_activity_page_displays_training_calendar(
        self, mock_title, mock_divider,
        mock_get_workouts, mock_get_dates, mock_get_events,
        mock_display_summary, mock_display_calendar, mock_display_recent, mock_display_share
    ):
        """Test that training calendar is displayed with calendar events."""
        events = [{'date': '2026-04-21', 'event': 'Race'}]
        mock_get_workouts.return_value = self._make_sample_workouts()
        mock_get_dates.return_value = []
        mock_get_events.return_value = events
        
        show_activity_page('user1')
        
        mock_display_calendar.assert_called_once_with(events)

    @patch('view.activity_page.display_share_progress')
    @patch('view.activity_page.display_recent_workouts')
    @patch('view.activity_page.display_training_calendar')
    @patch('view.activity_page.display_activity_summary')
    @patch('view.activity_page.get_all_calendar_events')
    @patch('view.activity_page.get_user_workout_dates')
    @patch('view.activity_page.get_user_workouts')
    @patch('streamlit.divider')
    @patch('streamlit.title')
    def test_show_activity_page_displays_recent_workouts(
        self, mock_title, mock_divider,
        mock_get_workouts, mock_get_dates, mock_get_events,
        mock_display_summary, mock_display_calendar, mock_display_recent, mock_display_share
    ):
        """Test that recent workouts are displayed."""
        workouts = self._make_sample_workouts()
        mock_get_workouts.return_value = workouts
        mock_get_dates.return_value = []
        mock_get_events.return_value = []
        
        show_activity_page('user1')
        
        mock_display_recent.assert_called_once_with(workouts)

    @patch('view.activity_page.display_share_progress')
    @patch('view.activity_page.display_recent_workouts')
    @patch('view.activity_page.display_training_calendar')
    @patch('view.activity_page.display_activity_summary')
    @patch('view.activity_page.get_all_calendar_events')
    @patch('view.activity_page.get_user_workout_dates')
    @patch('view.activity_page.get_user_workouts')
    @patch('streamlit.divider')
    @patch('streamlit.title')
    def test_show_activity_page_displays_share_progress(
        self, mock_title, mock_divider,
        mock_get_workouts, mock_get_dates, mock_get_events,
        mock_display_summary, mock_display_calendar, mock_display_recent, mock_display_share
    ):
        """Test that share progress feature is displayed."""
        workouts = self._make_sample_workouts()
        mock_get_workouts.return_value = workouts
        mock_get_dates.return_value = []
        mock_get_events.return_value = []
        
        show_activity_page('user1')
        
        mock_display_share.assert_called_once_with('user1', workouts)

    @patch('view.activity_page.display_share_progress')
    @patch('view.activity_page.display_recent_workouts')
    @patch('view.activity_page.display_training_calendar')
    @patch('view.activity_page.display_activity_summary')
    @patch('view.activity_page.get_all_calendar_events')
    @patch('view.activity_page.get_user_workout_dates')
    @patch('view.activity_page.get_user_workouts')
    @patch('streamlit.divider')
    @patch('streamlit.title')
    def test_show_activity_page_has_correct_dividers(
        self, mock_title, mock_divider,
        mock_get_workouts, mock_get_dates, mock_get_events,
        mock_display_summary, mock_display_calendar, mock_display_recent, mock_display_share
    ):
        """Test that dividers are displayed between all sections."""
        mock_get_workouts.return_value = self._make_sample_workouts()
        mock_get_dates.return_value = []
        mock_get_events.return_value = []
        
        show_activity_page('user1')
        
        # Should be 3 dividers: after summary, after calendar, after recent workouts
        self.assertEqual(mock_divider.call_count, 3)

    @patch('view.activity_page.display_share_progress')
    @patch('view.activity_page.display_recent_workouts')
    @patch('view.activity_page.display_training_calendar')
    @patch('view.activity_page.display_activity_summary')
    @patch('view.activity_page.get_all_calendar_events')
    @patch('view.activity_page.get_user_workout_dates')
    @patch('view.activity_page.get_user_workouts')
    @patch('streamlit.divider')
    @patch('streamlit.title')
    def test_show_activity_page_handles_no_workouts(
        self, mock_title, mock_divider,
        mock_get_workouts, mock_get_dates, mock_get_events,
        mock_display_summary, mock_display_calendar, mock_display_recent, mock_display_share
    ):
        """Test that page handles user with no workouts."""
        mock_get_workouts.return_value = []
        mock_get_dates.return_value = []
        mock_get_events.return_value = []
        
        show_activity_page('user_no_workouts')
        
        mock_display_summary.assert_called_once_with([])
        mock_display_recent.assert_called_once_with([])
        mock_display_share.assert_called_once_with('user_no_workouts', [])

    @patch('view.activity_page.display_share_progress')
    @patch('view.activity_page.display_recent_workouts')
    @patch('view.activity_page.display_training_calendar')
    @patch('view.activity_page.display_activity_summary')
    @patch('view.activity_page.get_all_calendar_events')
    @patch('view.activity_page.get_user_workout_dates')
    @patch('view.activity_page.get_user_workouts')
    @patch('streamlit.divider')
    @patch('streamlit.title')
    def test_show_activity_page_different_user_ids(
        self, mock_title, mock_divider,
        mock_get_workouts, mock_get_dates, mock_get_events,
        mock_display_summary, mock_display_calendar, mock_display_recent, mock_display_share
    ):
        """Test that page correctly uses different user IDs."""
        mock_get_workouts.return_value = self._make_sample_workouts()
        mock_get_dates.return_value = []
        mock_get_events.return_value = []
        
        # Test with user1
        show_activity_page('user1')
        self.assertEqual(mock_get_workouts.call_args_list[0][0][0], 'user1')
        self.assertEqual(mock_get_dates.call_args_list[0][0][0], 'user1')
        self.assertEqual(mock_get_events.call_args_list[0][0][0], 'user1')
        
        # Reset mocks
        mock_get_workouts.reset_mock()
        mock_get_dates.reset_mock()
        mock_get_events.reset_mock()
        
        # Test with user2
        show_activity_page('user2')
        self.assertEqual(mock_get_workouts.call_args_list[0][0][0], 'user2')
        self.assertEqual(mock_get_dates.call_args_list[0][0][0], 'user2')
        self.assertEqual(mock_get_events.call_args_list[0][0][0], 'user2')


if __name__ == '__main__':
    unittest.main()
