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
# Block written by ChatGPT
    @patch('streamlit.divider')
    @patch('streamlit.image')
    @patch('streamlit.write')
    @patch('streamlit.caption')
    @patch('streamlit.columns')
    def test_display_post_renders_content(
        self, mock_columns, mock_caption, mock_write, mock_image, mock_divider
    ):
# Block written by ChatGPT
        mock_col1 = unittest.mock.MagicMock()
        mock_col2 = unittest.mock.MagicMock()
        mock_columns.return_value = [mock_col1, mock_col2]

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
        mock_columns.return_value = [mock_col1, mock_col2]

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

    def test_foo(self):
        """Tests foo."""
        pass


class TestDisplayRecentWorkouts(unittest.TestCase):
    """Tests the display_recent_workouts function."""

    def test_foo(self):
        """Tests foo."""
        pass


if __name__ == "__main__":
    unittest.main()
