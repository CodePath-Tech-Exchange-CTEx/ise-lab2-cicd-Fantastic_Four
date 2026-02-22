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
    """Tests the display_post function."""

    def test_foo(self):
        """Tests foo."""
        pass


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
