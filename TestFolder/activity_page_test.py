import unittest
from unittest.mock import patch, MagicMock
import os


os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "dummy_path.json"

from view.activity_page import show_activity_page

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
        # Parche global para la autenticación de Google
        self.auth_patcher = patch('google.auth.default', return_value=(MagicMock(), "project-id"))
        self.auth_patcher.start()

        self.patchers = [
            patch('view.activity_page.st'),
            patch('view.activity_page.get_user_workouts'),
            patch('view.activity_page.get_user_workout_dates'), 
            patch('view.activity_page.create_shared_post'),
            patch('view.activity_page.update_streak'),
            patch('view.activity_page.display_activity_summary'),
            patch('view.activity_page.display_recent_workouts'),
            patch('view.activity_page.calendar'),
            # CRÍTICO: Parcheamos la función que llama a BigQuery para evitar el error 401
            patch('view.activity_page.get_all_calendar_events')
        ]
        
        self.mocks = [p.start() for p in self.patchers]
        (self.mock_st, self.mock_get_workouts, self.mock_get_dates, 
         self.mock_create_post, self.mock_update_streak, 
         self.mock_disp_summary, self.mock_disp_recent, 
         self.mock_calendar, self.mock_get_calendar_events) = self.mocks

        # Configuración de retornos de los mocks
        self.mock_get_workouts.return_value = DataFactory.workouts()
        self.mock_get_dates.return_value = ["2026-04-15", "2026-04-16"]
        self.mock_get_calendar_events.return_value = [] # Simulamos calendario vacío
        self.mock_st.selectbox.return_value = "Steps"

    def tearDown(self):
        for p in self.patchers:
            p.stop()
        self.auth_patcher.stop()

    def test_stat_selection_logic_steps(self):
        """Verify the default message generated for 'Steps' selection."""
        self.mock_st.selectbox.return_value = "Steps"
        
        show_activity_page('user123')
        
        # Obtenemos los argumentos de la llamada a text_area
        self.assertTrue(self.mock_st.text_area.called, "text_area should have been called")
        args, kwargs = self.mock_st.text_area.call_args
        
        # Verificamos el contenido del mensaje
        actual_value = kwargs.get('value') if kwargs.get('value') else args[0]
        self.assertIn("7,000 total steps", actual_value)

    def test_share_button_workflow(self):
        """Test the full share flow: Button click -> Backend Call -> UI Feedback."""
        self.mock_st.selectbox.return_value = "Distance"
        self.mock_st.text_area.return_value = "I just covered 6.5 km!"
        self.mock_st.button.return_value = True 
        
        show_activity_page('user_99')
        
        # Verificamos que se llame a la lógica de compartir y actualizar racha
        self.mock_create_post.assert_called_once_with('user_99', "I just covered 6.5 km!")
        self.mock_update_streak.assert_called_once_with('user_99')
        self.mock_st.success.assert_called_once()
        self.mock_st.balloons.assert_called_once()

if __name__ == '__main__':
    unittest.main()