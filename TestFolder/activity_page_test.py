import unittest
from unittest.mock import patch, MagicMock
from view.activity_page import show_activity_page

# 1. Ajustamos la fábrica para usar las llaves EXACTAS de tu código
class DataFactory:
    @staticmethod
    def workouts():
        """Returns a sample list of workout dictionaries."""
        return [
            {
                "UserId": "user_99",
                "WorkoutType": "Swimming",
                "steps": 3500,           
                "calories_burned": 250, 
                "distance": 1.5,
                "StartTimestamp": "2026-04-16 10:00:00"
            },
            {
                "UserId": "user_99",
                "WorkoutType": "Running",
                "steps": 3500,           
                "calories_burned": 250,
                "distance": 5.0,
                "StartTimestamp": "2026-04-15 08:30:00"
            }
        ]

class TestShowActivityPage(unittest.TestCase):

    def setUp(self):
        self.patchers = [
            patch('view.activity_page.st'),
            patch('view.activity_page.get_user_workouts'),
            patch('view.activity_page.get_user_workout_dates'), 
            patch('view.activity_page.create_shared_post'),
            patch('view.activity_page.update_streak'),
            patch('view.activity_page.display_activity_summary'),
            patch('view.activity_page.display_recent_workouts'),
            patch('view.activity_page.calendar')
        ]
        
       
        self.mocks = [p.start() for p in self.patchers]
        (self.mock_st, self.mock_get_workouts, self.mock_get_dates, 
         self.mock_create_post, self.mock_update_streak, 
         self.mock_disp_summary, self.mock_disp_recent, self.mock_calendar) = self.mocks

        
        self.mock_get_workouts.return_value = DataFactory.workouts()
        self.mock_get_dates.return_value = ["2026-04-15", "2026-04-16"]

    def tearDown(self):
        for p in self.patchers:
            p.stop()

    def test_stat_selection_logic_steps(self):
        """Verify the default message generated for 'Steps' selection."""
        self.mock_st.selectbox.return_value = "Steps"
        
        show_activity_page('user123')
        
        
        args, kwargs = self.mock_st.text_area.call_args
        

        actual_value = kwargs.get('value')
        self.assertIn("7,000 total steps", actual_value)

    def test_share_button_workflow(self):
        """Test the full share flow: Button click -> Backend Call -> UI Feedback."""
        self.mock_st.selectbox.return_value = "Distance"
        self.mock_st.text_area.return_value = "I just covered 6.5 km!"
        self.mock_st.button.return_value = True 
        
        show_activity_page('user_99')
        
      
        self.mock_create_post.assert_called_once_with('user_99', "I just covered 6.5 km!")
        self.mock_update_streak.assert_called_once_with('user_99')
        self.mock_st.success.assert_called_once()
        self.mock_st.balloons.assert_called_once()

if __name__ == '__main__':
    unittest.main()