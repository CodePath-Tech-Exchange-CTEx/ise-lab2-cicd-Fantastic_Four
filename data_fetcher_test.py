#############################################################################
# data_fetcher_test.py
#
# This file contains tests for data_fetcher.py.
#
# You will write these tests in Unit 3.
#############################################################################

import unittest
from unittest.mock import patch, MagicMock
import datetime
from data_fetcher import (
    get_user_sensor_data,
    get_user_workouts,
    get_user_profile,
    get_user_posts,
    get_genai_advice
)

class TestDataFetcher(unittest.TestCase):
    
    @patch('data_fetcher.bigquery.Client')
    def test_get_user_sensor_data(self, MockBigQueryClient):
        # 1. Setup the mock
        mock_client = MockBigQueryClient.return_value
        mock_query_job = MagicMock()
        
        # Create a fake row that acts like a BigQuery row object
        mock_row = MagicMock()
        mock_row.SensorId = 'sensor_1'
        mock_row.WorkoutID = 'workout_1'
        mock_row.Timestamp = '2026-03-23T10:00:00Z'
        mock_row.SensorValue = 120.5

        # Set the mock to return our fake row when result() is called
        mock_query_job.result.return_value = [mock_row]
        mock_client.query.return_value = mock_query_job

        # 2. Call the function
        result = get_user_sensor_data('user_123', 'workout_1')

        # 3. Assertions
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]['SensorId'], 'sensor_1')
        self.assertEqual(result[0]['WorkoutID'], 'workout_1')
        self.assertEqual(result[0]['Timestamp'], '2026-03-23T10:00:00Z')
        self.assertEqual(result[0]['SensorValue'], 120.5)
        # Verify the query was actually called
        mock_client.query.assert_called_once()

    @patch('data_fetcher.bigquery.Client')
    def test_get_user_workouts(self, MockBigQueryClient):
        # 1. Setup the mock
        mock_client = MockBigQueryClient.return_value
        mock_query_job = MagicMock()
        
        mock_row = MagicMock()
        mock_row.WorkoutId = 'workout_1'
        mock_row.StartTimestamp = '2026-03-23T09:00:00Z'
        mock_row.TotalDistance = 5.2
        mock_row.TotalSteps = 6000
        mock_row.CaloriesBurned = 450
        
        mock_query_job.result.return_value = [mock_row]
        mock_client.query.return_value = mock_query_job

        # 2. Call the function
        result = get_user_workouts('user_123')

        # 3. Assertions
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]['workout_id'], 'workout_1')
        self.assertEqual(result[0]['distance'], 5.2)
        self.assertEqual(result[0]['calories_burned'], 450)

    @patch('data_fetcher.bigquery.Client')
    def test_get_user_profile(self, MockBigQueryClient):
        # 1. Setup the mock
        mock_client = MockBigQueryClient.return_value
        
        # Because this function makes TWO queries, we need two separate mock jobs
        mock_job_users = MagicMock()
        mock_job_friends = MagicMock()
        
        # Fake User Row
        mock_user_row = MagicMock()
        mock_user_row.Name = "Test User"
        mock_user_row.Username = "test_user_99"
        mock_user_row.DateOfBirth = "1995-05-05"
        mock_user_row.ImageUrl = "http://example.com/pic.jpg"
        
        # Fake Friend Row
        mock_friend_row = MagicMock()
        mock_friend_row.UserId2 = "friend_abc"
        
        mock_job_users.result.return_value = [mock_user_row]
        mock_job_friends.result.return_value = [mock_friend_row]
        
        # side_effect allows us to return different things each time client.query() is called
        mock_client.query.side_effect = [mock_job_users, mock_job_friends]

        # 2. Call the function
        result = get_user_profile('user_123')

        # 3. Assertions
        self.assertEqual(result['full_name'], "Test User")
        self.assertEqual(result['username'], "test_user_99")
        self.assertEqual(result['profile_image'], "http://example.com/pic.jpg")
        self.assertEqual(result['friends'], ["friend_abc"])
        self.assertEqual(mock_client.query.call_count, 2)

    @patch('data_fetcher.get_user_profile') # Mock the internal function call
    @patch('data_fetcher.bigquery.Client')
    def test_get_user_posts(self, MockBigQueryClient, mock_get_user_profile):
        # 1. Setup the mocks
        mock_client = MockBigQueryClient.return_value
        mock_query_job = MagicMock()
        
        # Mock what BigQuery returns for posts
        mock_post_row = MagicMock()
        mock_post_row.Timestamp = '2026-03-23T12:00:00Z'
        mock_post_row.Content = 'Just finished a great run!'
        mock_post_row.ImageUrl = 'http://example.com/post_pic.jpg'
        
        mock_query_job.result.return_value = [mock_post_row]
        mock_client.query.return_value = mock_query_job
        
        # Mock what our internal get_user_profile returns
        mock_get_user_profile.return_value = {
            "username": "runner_guy",
            "profile_image": "http://example.com/profile.jpg"
        }

        # 2. Call the function
        result = get_user_posts('user_123')

        # 3. Assertions
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]['content'], 'Just finished a great run!')
        self.assertEqual(result[0]['post_image'], 'http://example.com/post_pic.jpg')
        # Ensure the profile data was stitched in properly
        self.assertEqual(result[0]['username'], 'runner_guy')
        self.assertEqual(result[0]['user_image'], 'http://example.com/profile.jpg')

    @patch('data_fetcher.GenerativeModel')
    @patch('data_fetcher.vertexai.init')
    def test_get_genai_advice(self, mock_vertex_init, MockGenerativeModel):
        # 1. Setup the mocks
        mock_model_instance = MagicMock()
        mock_ai_response = MagicMock()
        
        # Simulate the text the AI would generate
        mock_ai_response.text = "Consistency is the key to progress!"
        mock_model_instance.generate_content.return_value = mock_ai_response
        MockGenerativeModel.return_value = mock_model_instance

        # 2. Call the function
        result = get_genai_advice('user_123')

        # 3. Assertions
        mock_vertex_init.assert_called_once_with(project="kevin-beltran-pena-uprm", location="us-central1")
        self.assertEqual(result['advice_id'], 'ai_advice_1')
        self.assertEqual(result['content'], "Consistency is the key to progress!")
        self.assertIsNone(result['image'])
        self.assertIn('timestamp', result)

if __name__ == "__main__":
    unittest.main()