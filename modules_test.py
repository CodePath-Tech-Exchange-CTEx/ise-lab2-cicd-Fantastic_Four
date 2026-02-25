#############################################################################
# modules_test.py
#
# This file contains tests for modules.py.
#
# You will write these tests in Unit 2.
#############################################################################

import unittest
from streamlit.testing.v1 import AppTest
from modules import display_post, display_activity_summary, display_genai_advice, display_recent_workouts
from unittest.mock import patch # import patch 

# Write your tests below

class TestDisplayPost(unittest.TestCase):

    @patch('streamlit.divider')
    @patch('streamlit.image')
    @patch('streamlit.write')
    @patch('streamlit.caption')
    @patch('streamlit.columns')
    def test_display_post_renders_content(
        self, mock_columns, mock_caption, mock_write, mock_image, mock_divider
    ):
        mock_col1 = unittest.mock.MagicMock()
        mock_col2 = unittest.mock.MagicMock()

        mock_col1.__enter__.return_value = mock_col1
        mock_col1.__exit__.return_value = None
        mock_col2.__enter__.return_value = mock_col2
        mock_col2.__exit__.return_value = None

        mock_columns.return_value = (mock_col1, mock_col2)

        username = "Amari"
        user_image = "profile.png"
        timestamp = "Today"
        content = "This is a test post."
        post_image = "post.png"

        display_post(username, user_image, timestamp, content, post_image)

        mock_columns.assert_called_once()
        mock_caption.assert_called_with(timestamp)
        mock_write.assert_any_call(f"**{username}**")
        mock_write.assert_any_call(content)
        self.assertTrue(mock_image.called)
        mock_divider.assert_called_once()

    @patch('streamlit.divider')
    @patch('streamlit.image')
    @patch('streamlit.write')
    @patch('streamlit.caption')
    @patch('streamlit.columns')
    def test_display_post_without_image(
        self, mock_columns, mock_caption, mock_write, mock_image, mock_divider
    ):
        mock_col1 = unittest.mock.MagicMock()
        mock_col2 = unittest.mock.MagicMock()

        mock_col1.__enter__.return_value = mock_col1
        mock_col1.__exit__.return_value = None
        mock_col2.__enter__.return_value = mock_col2
        mock_col2.__exit__.return_value = None

        mock_columns.return_value = (mock_col1, mock_col2)

        display_post(
            "Amari",
            "profile.png",
            "Today",
            "No image post",
            None
        )

        self.assertEqual(mock_image.call_count, 1)
        mock_divider.assert_called_once()


class TestDisplayActivitySummary(unittest.TestCase):
    """Tests the display_activity_summary function."""

    @patch('streamlit.metric') # This "fakes" the st.metric function
    @patch('streamlit.subheader')
    
    def test_display_activity_summary_data_accuracy(self, mock_subheader, mock_metric):

        # Setup
        test_workouts = [
            {'calories_burned': 500, 'distance': 3.5, 'steps': 7000},
            {'calories_burned': 200, 'distance': 1.5, 'steps': 3000}
        ]
            
        # Execute
        display_activity_summary(test_workouts)
        
        # Assert (Checking if the math was correct!)
        # We expect 3 calls to st.metric (Calories, Distance, Steps)
        self.assertEqual(mock_metric.call_count, 3)
        
        # Check if the first call (Calories) received the sum (700)
        # Note: adjust the 'value' check based on if you added "kcal" strings or not
        args, kwargs = mock_metric.call_args_list[0]
        self.assertEqual(kwargs['label'], "Total Calories")
        self.assertEqual(kwargs['value'], "700 kcal")


class TestDisplayGenAiAdvice(unittest.TestCase):
    """Tests the display_genai_advice function."""
    @patch('streamlit.subheader')
    @patch('streamlit.caption')
    @patch('streamlit.write')
    @patch('streamlit.image')
    def test_display_genAI_advice(self,mock_image, mock_write, mock_caption, mock_subheader):
        """Tests the function displayGEnAIAdvice with all the elements"""
        timestamp= "2024-01-01 00:00:00"
        content= "You are doing greta!!!"
        image_url= "https://example.com?motivation.jpg"

        display_genai_advice(timestamp, content, image_url)

        mock_subheader.assert_called_once_with("GenAI Advice")
        mock_caption.assert_called_once_with(timestamp)
        mock_write.assert_called_once_with(content)
        mock_image.assert_called_once_with(image_url, width="stretch")

    @patch('streamlit.subheader')
    @patch('streamlit.caption')
    @patch('streamlit.write')
    @patch('streamlit.image')
    def test_display_genAI_advice_no_image(self,mock_image, mock_write, mock_caption,mock_subheader):
        """Tests the function displayGenAIAdvice with no image"""
        display_genai_advice("2024-01-01","Example", None)

        mock_subheader.assert_called_once_with("GenAI Advice")
        mock_caption.assert_called_once_with("2024-01-01")
        mock_write.assert_called_once_with("Example")
        mock_image.assert_not_called()
    




class TestDisplayRecentWorkouts(unittest.TestCase):
    def test_display_with_valid_data(self):
        """Tests that the function handles a list of workout dictionaries."""
        # Mock data representing what comes from data_fetcher.py
        mock_workouts = [
            {
                'start_timestamp': '2026-02-20 08:30:00',
                'distance': 3.5,
                'steps': 4200,
                'calories_burned': 210
            },
            {
                'start_timestamp': '2026-02-21 17:00:00',
                'distance': 1.2,
                'steps': 1500,
                'calories_burned': 85
            }
        ]
        
        # This checks if the function runs without raising an Exception
        try:
            display_recent_workouts(mock_workouts)
        except Exception as e:
            self.fail(f"display_recent_workouts raised {type(e).__name__} unexpectedly!") # Line written by Gemini

    def test_display_empty_list(self):
        """Tests that the function handles an empty list without crashing."""
        try:
            display_recent_workouts([])
        except Exception as e:
            self.fail(f"display_recent_workouts crashed on empty list: {e}") # Line written by Gemini


if __name__ == "__main__":
    unittest.main()
