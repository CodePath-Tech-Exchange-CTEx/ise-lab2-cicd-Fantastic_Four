#############################################################################
# data_fetcher_test.py
#
# Unit tests for data_fetcher.py.
# All BigQuery and Vertex AI calls are mocked so tests run without GCP access.
#############################################################################

import unittest
from unittest.mock import patch, MagicMock, call
import datetime

from data_fetcher import (
    get_user_sensor_data,
    get_user_workouts,
    get_user_profile,
    get_user_posts,
    get_genai_advice,
    create_shared_post,
    get_streak,
    update_streak
    
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_bq_client_mock(rows_per_query):
    """
    Returns a mock bigquery.Client() whose .query().result() calls return
    successive row lists from rows_per_query (a list of lists).
    """
    mock_client   = MagicMock()
    mock_jobs     = []

    for rows in rows_per_query:
        job = MagicMock()
        job.result.return_value = rows
        mock_jobs.append(job)

    mock_client.query.side_effect = mock_jobs
    return mock_client


# ---------------------------------------------------------------------------
# get_user_sensor_data
# ---------------------------------------------------------------------------

class TestGetUserSensorData(unittest.TestCase):

    @patch('data_fetcher.bigquery.Client')
    def test_returns_correctly_keyed_dicts(self, MockClient):
        row = MagicMock()
        row.sensor_type = 'Heart Rate'
        row.timestamp   = datetime.datetime(2024, 7, 29, 7, 15)
        row.data        = 120.0
        row.units       = 'bpm'

        MockClient.return_value = _make_bq_client_mock([[row]])

        result = get_user_sensor_data('user1', 'workout1')

        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]['sensor_type'], 'Heart Rate')
        self.assertEqual(result[0]['data'],        120.0)
        self.assertEqual(result[0]['units'],       'bpm')
        self.assertEqual(result[0]['timestamp'],   datetime.datetime(2024, 7, 29, 7, 15))

    @patch('data_fetcher.bigquery.Client')
    def test_returns_empty_list_when_no_rows(self, MockClient):
        MockClient.return_value = _make_bq_client_mock([[]])
        result = get_user_sensor_data('user1', 'workout_missing')
        self.assertEqual(result, [])

    @patch('data_fetcher.bigquery.Client')
    def test_returns_multiple_sensor_rows(self, MockClient):
        rows = []
        for i in range(3):
            r = MagicMock()
            r.sensor_type = f'Sensor {i}'
            r.timestamp   = datetime.datetime(2024, 7, 29, 7, i * 15)
            r.data        = float(i * 10)
            r.units       = 'units'
            rows.append(r)

        MockClient.return_value = _make_bq_client_mock([rows])
        result = get_user_sensor_data('user1', 'workout1')

        self.assertEqual(len(result), 3)
        # Confirm all required keys are present on every entry
        for entry in result:
            self.assertIn('sensor_type', entry)
            self.assertIn('timestamp',   entry)
            self.assertIn('data',        entry)
            self.assertIn('units',       entry)

    @patch('data_fetcher.bigquery.Client')
    def test_query_is_called_once(self, MockClient):
        MockClient.return_value = _make_bq_client_mock([[]])
        get_user_sensor_data('user1', 'workout1')
        MockClient.return_value.query.assert_called_once()

    @patch('data_fetcher.bigquery.Client')
    def test_does_not_include_raw_sensor_id_key(self, MockClient):
        """Output dicts must use spec-defined keys, not raw BigQuery column names."""
        row = MagicMock()
        row.sensor_type = 'Step Count'
        row.timestamp   = datetime.datetime(2024, 7, 29, 7, 30)
        row.data        = 3000.0
        row.units       = 'steps'

        MockClient.return_value = _make_bq_client_mock([[row]])
        result = get_user_sensor_data('user1', 'workout1')

        self.assertNotIn('SensorId',    result[0])
        self.assertNotIn('SensorValue', result[0])


# ---------------------------------------------------------------------------
# get_user_workouts
# ---------------------------------------------------------------------------

class TestGetUserWorkouts(unittest.TestCase):

    def _make_workout_row(self):
        row = MagicMock()
        row.WorkoutId          = 'workout1'
        row.StartTimestamp     = datetime.datetime(2024, 7, 29, 7, 0)
        row.EndTimestamp       = datetime.datetime(2024, 7, 29, 8, 0)
        row.StartLocationLat   = 37.7749
        row.StartLocationLong  = -122.4194
        row.EndLocationLat     = 37.8049
        row.EndLocationLong    = -122.4210
        row.TotalDistance      = 5.0
        row.TotalSteps         = 8000
        row.CaloriesBurned     = 400.0
        return row

    @patch('data_fetcher.bigquery.Client')
    def test_all_required_keys_present(self, MockClient):
        MockClient.return_value = _make_bq_client_mock([[self._make_workout_row()]])
        result = get_user_workouts('user1')

        self.assertEqual(len(result), 1)
        w = result[0]
        for key in ('workout_id', 'start_timestamp', 'end_timestamp',
                    'start_lat_lng', 'end_lat_lng', 'distance', 'steps', 'calories_burned'):
            self.assertIn(key, w, msg=f"Missing key: {key}")

    @patch('data_fetcher.bigquery.Client')
    def test_values_mapped_correctly(self, MockClient):
        MockClient.return_value = _make_bq_client_mock([[self._make_workout_row()]])
        result = get_user_workouts('user1')

        self.assertEqual(result[0]['workout_id'],      'workout1')
        self.assertEqual(result[0]['distance'],        5.0)
        self.assertEqual(result[0]['steps'],           8000)
        self.assertEqual(result[0]['calories_burned'], 400.0)
        self.assertEqual(result[0]['start_lat_lng'],   (37.7749, -122.4194))
        self.assertEqual(result[0]['end_lat_lng'],     (37.8049, -122.4210))

    @patch('data_fetcher.bigquery.Client')
    def test_null_location_becomes_none(self, MockClient):
        row = self._make_workout_row()
        row.StartLocationLat  = None
        row.StartLocationLong = None
        row.EndLocationLat    = None
        row.EndLocationLong   = None

        MockClient.return_value = _make_bq_client_mock([[row]])
        result = get_user_workouts('user1')

        self.assertIsNone(result[0]['start_lat_lng'])
        self.assertIsNone(result[0]['end_lat_lng'])

    @patch('data_fetcher.bigquery.Client')
    def test_empty_list_when_no_workouts(self, MockClient):
        MockClient.return_value = _make_bq_client_mock([[]])
        self.assertEqual(get_user_workouts('user_nobody'), [])

    @patch('data_fetcher.bigquery.Client')
    def test_multiple_workouts_returned(self, MockClient):
        rows = [self._make_workout_row(), self._make_workout_row()]
        rows[1].WorkoutId = 'workout2'
        MockClient.return_value = _make_bq_client_mock([rows])
        result = get_user_workouts('user1')
        self.assertEqual(len(result), 2)


# ---------------------------------------------------------------------------
# get_user_profile
# ---------------------------------------------------------------------------

class TestGetUserProfile(unittest.TestCase):

    def _make_user_row(self):
        row = MagicMock()
        row.Name        = 'Alice Johnson'
        row.Username    = 'alicej'
        row.DateOfBirth = datetime.date(1990, 1, 15)
        row.ImageUrl    = 'http://example.com/alice.jpg'
        return row

    def _make_friend_row(self, friend_id):
        row = MagicMock()
        # UNION query returns first column regardless of alias; support both
        row.UserId2 = friend_id
        row.__getitem__ = lambda self, i: friend_id
        return row

    @patch('data_fetcher.bigquery.Client')
    def test_all_required_keys_present(self, MockClient):
        friend = self._make_friend_row('user2')
        MockClient.return_value = _make_bq_client_mock(
            [[self._make_user_row()], [friend]]
        )
        result = get_user_profile('user1')

        for key in ('full_name', 'username', 'date_of_birth', 'profile_image', 'friends'):
            self.assertIn(key, result, msg=f"Missing key: {key}")

    @patch('data_fetcher.bigquery.Client')
    def test_values_mapped_correctly(self, MockClient):
        friend = self._make_friend_row('user2')
        MockClient.return_value = _make_bq_client_mock(
            [[self._make_user_row()], [friend]]
        )
        result = get_user_profile('user1')

        self.assertEqual(result['full_name'],     'Alice Johnson')
        self.assertEqual(result['username'],      'alicej')
        self.assertEqual(result['profile_image'], 'http://example.com/alice.jpg')

    @patch('data_fetcher.bigquery.Client')
    def test_friends_list_populated(self, MockClient):
        friends = [self._make_friend_row('user2'), self._make_friend_row('user3')]
        MockClient.return_value = _make_bq_client_mock(
            [[self._make_user_row()], friends]
        )
        result = get_user_profile('user1')
        self.assertIn('user2', result['friends'])

    @patch('data_fetcher.bigquery.Client')
    def test_no_friends_returns_empty_list(self, MockClient):
        MockClient.return_value = _make_bq_client_mock(
            [[self._make_user_row()], []]
        )
        result = get_user_profile('user1')
        self.assertEqual(result['friends'], [])

    @patch('data_fetcher.bigquery.Client')
    def test_two_queries_are_made(self, MockClient):
        MockClient.return_value = _make_bq_client_mock(
            [[self._make_user_row()], []]
        )
        get_user_profile('user1')
        self.assertEqual(MockClient.return_value.query.call_count, 2)


# ---------------------------------------------------------------------------
# get_user_posts
# ---------------------------------------------------------------------------

class TestGetUserPosts(unittest.TestCase):

    @patch('data_fetcher.get_user_profile')
    @patch('data_fetcher.bigquery.Client')
    def test_all_required_keys_present(self, MockClient, mock_profile):
        mock_profile.return_value = {
            'username': 'alicej', 'profile_image': 'http://example.com/alice.jpg'
        }
        row = MagicMock()
        row.PostId    = 'post1'
        row.Timestamp = datetime.datetime(2024, 7, 29, 12, 0)
        row.Content   = 'Great run today!'
        row.ImageUrl  = 'http://example.com/post1.jpg'

        MockClient.return_value = _make_bq_client_mock([[row]])
        result = get_user_posts('user1')

        self.assertEqual(len(result), 1)
        for key in ('user_id', 'post_id', 'username', 'user_image',
                    'timestamp', 'content', 'post_image'):
            self.assertIn(key, result[0], msg=f"Missing key: {key}")

    @patch('data_fetcher.get_user_profile')
    @patch('data_fetcher.bigquery.Client')
    def test_profile_data_stitched_in(self, MockClient, mock_profile):
        mock_profile.return_value = {
            'username': 'alicej', 'profile_image': 'http://example.com/alice.jpg'
        }
        row = MagicMock()
        row.PostId    = 'post1'
        row.Timestamp = datetime.datetime(2024, 7, 29, 12, 0)
        row.Content   = 'Just finished!'
        row.ImageUrl  = None

        MockClient.return_value = _make_bq_client_mock([[row]])
        result = get_user_posts('user1')

        self.assertEqual(result[0]['username'],   'alicej')
        self.assertEqual(result[0]['user_image'], 'http://example.com/alice.jpg')
        self.assertEqual(result[0]['user_id'],    'user1')
        self.assertEqual(result[0]['post_id'],    'post1')

    @patch('data_fetcher.get_user_profile')
    @patch('data_fetcher.bigquery.Client')
    def test_empty_list_when_no_posts(self, MockClient, mock_profile):
        mock_profile.return_value = {'username': 'alicej', 'profile_image': ''}
        MockClient.return_value   = _make_bq_client_mock([[]])
        self.assertEqual(get_user_posts('user1'), [])

    @patch('data_fetcher.get_user_profile')
    @patch('data_fetcher.bigquery.Client')
    def test_null_image_handled(self, MockClient, mock_profile):
        mock_profile.return_value = {'username': 'alicej', 'profile_image': ''}
        row = MagicMock()
        row.PostId    = 'post1'
        row.Timestamp = datetime.datetime(2024, 7, 29, 12, 0)
        row.Content   = 'Text only post'
        row.ImageUrl  = None

        MockClient.return_value = _make_bq_client_mock([[row]])
        result = get_user_posts('user1')

        self.assertIsNone(result[0]['post_image'])


# ---------------------------------------------------------------------------
# get_genai_advice
# ---------------------------------------------------------------------------

class TestGetGenaiAdvice(unittest.TestCase):

    @patch('data_fetcher.get_user_workouts')
    @patch('data_fetcher.get_user_profile')
    @patch('data_fetcher.GenerativeModel')
    @patch('data_fetcher.vertexai.init')
    def test_all_required_keys_present(self, mock_init, MockModel,
                                       mock_profile, mock_workouts):
        mock_profile.return_value  = {'full_name': 'Alice', 'username': 'alicej',
                                      'date_of_birth': '1990-01-15',
                                      'profile_image': '', 'friends': []}
        mock_workouts.return_value = [{'steps': 8000, 'calories_burned': 400,
                                       'workout_id': 'w1', 'start_timestamp': None,
                                       'end_timestamp': None, 'start_lat_lng': None,
                                       'end_lat_lng': None, 'distance': 5.0}]
        response      = MagicMock()
        response.text = 'Keep pushing, you are doing great!'
        MockModel.return_value.generate_content.return_value = response

        result = get_genai_advice('user1')

        for key in ('advice_id', 'timestamp', 'content', 'image'):
            self.assertIn(key, result, msg=f"Missing key: {key}")

    @patch('data_fetcher.get_user_workouts')
    @patch('data_fetcher.get_user_profile')
    @patch('data_fetcher.GenerativeModel')
    @patch('data_fetcher.vertexai.init')
    def test_content_comes_from_model(self, mock_init, MockModel,
                                      mock_profile, mock_workouts):
        mock_profile.return_value  = {'full_name': 'Alice', 'username': 'alicej',
                                      'date_of_birth': '', 'profile_image': '', 'friends': []}
        mock_workouts.return_value = []
        response      = MagicMock()
        response.text = 'Every step counts!'
        MockModel.return_value.generate_content.return_value = response

        result = get_genai_advice('user1')
        self.assertEqual(result['content'], 'Every step counts!')

    @patch('data_fetcher.get_user_workouts')
    @patch('data_fetcher.get_user_profile')
    @patch('data_fetcher.GenerativeModel')
    @patch('data_fetcher.vertexai.init')
    def test_advice_id_is_unique_each_call(self, mock_init, MockModel,
                                           mock_profile, mock_workouts):
        mock_profile.return_value  = {'full_name': 'Alice', 'username': 'alicej',
                                      'date_of_birth': '', 'profile_image': '', 'friends': []}
        mock_workouts.return_value = []
        response      = MagicMock()
        response.text = 'Go!'
        MockModel.return_value.generate_content.return_value = response

        result1 = get_genai_advice('user1')
        result2 = get_genai_advice('user1')
        self.assertNotEqual(result1['advice_id'], result2['advice_id'])

    @patch('data_fetcher.random.random', return_value=0.10)   # < 0.30 → image included
    @patch('data_fetcher.get_user_workouts')
    @patch('data_fetcher.get_user_profile')
    @patch('data_fetcher.GenerativeModel')
    @patch('data_fetcher.vertexai.init')
    def test_image_included_when_random_below_threshold(
            self, mock_init, MockModel, mock_profile, mock_workouts, mock_random):
        mock_profile.return_value  = {'full_name': 'Alice', 'username': 'alicej',
                                      'date_of_birth': '', 'profile_image': '', 'friends': []}
        mock_workouts.return_value = []
        response      = MagicMock()
        response.text = 'Go!'
        MockModel.return_value.generate_content.return_value = response

        result = get_genai_advice('user1')
        self.assertIsNotNone(result['image'])

    @patch('data_fetcher.random.random', return_value=0.99)   # > 0.30 → no image
    @patch('data_fetcher.get_user_workouts')
    @patch('data_fetcher.get_user_profile')
    @patch('data_fetcher.GenerativeModel')
    @patch('data_fetcher.vertexai.init')
    def test_image_none_when_random_above_threshold(
            self, mock_init, MockModel, mock_profile, mock_workouts, mock_random):
        mock_profile.return_value  = {'full_name': 'Alice', 'username': 'alicej',
                                      'date_of_birth': '', 'profile_image': '', 'friends': []}
        mock_workouts.return_value = []
        response      = MagicMock()
        response.text = 'Go!'
        MockModel.return_value.generate_content.return_value = response

        result = get_genai_advice('user1')
        self.assertIsNone(result['image'])

    @patch('data_fetcher.get_user_workouts')
    @patch('data_fetcher.get_user_profile')
    @patch('data_fetcher.GenerativeModel')
    @patch('data_fetcher.vertexai.init')
    def test_vertex_initialized_with_correct_project(
            self, mock_init, MockModel, mock_profile, mock_workouts):
        mock_profile.return_value  = {'full_name': 'Alice', 'username': 'alicej',
                                      'date_of_birth': '', 'profile_image': '', 'friends': []}
        mock_workouts.return_value = []
        response      = MagicMock()
        response.text = 'Go!'
        MockModel.return_value.generate_content.return_value = response

        get_genai_advice('user1')
        mock_init.assert_called_once_with(
            project="kevin-beltran-pena-uprm", location="us-central1"
        )


# ---------------------------------------------------------------------------
# create_shared_post
# ---------------------------------------------------------------------------

class TestCreateSharedPost(unittest.TestCase):

    @patch('data_fetcher.bigquery.Client')
    def test_query_is_executed(self, MockClient):
        mock_client = MagicMock()
        mock_job    = MagicMock()
        mock_client.query.return_value = mock_job
        MockClient.return_value        = mock_client

        create_shared_post('user1', 'I just walked 8000 steps!')

        mock_client.query.assert_called_once()
        mock_job.result.assert_called_once()

    @patch('data_fetcher.bigquery.Client')
    def test_query_contains_user_id_and_content(self, MockClient):
        mock_client = MagicMock()
        mock_job    = MagicMock()
        mock_client.query.return_value = mock_job
        MockClient.return_value        = mock_client

        create_shared_post('user1', 'Great workout!')

        executed_query = mock_client.query.call_args[0][0]
        self.assertIn('user1',        executed_query)
        self.assertIn('Great workout', executed_query)

    @patch('data_fetcher.bigquery.Client')
    def test_inserts_into_posts_table(self, MockClient):
        mock_client = MagicMock()
        mock_job    = MagicMock()
        mock_client.query.return_value = mock_job
        MockClient.return_value        = mock_client

        create_shared_post('user1', 'Test post.')

        executed_query = mock_client.query.call_args[0][0]
        self.assertIn('INSERT', executed_query.upper())
        self.assertIn('Posts',  executed_query)

    @patch('data_fetcher.bigquery.Client')
    def test_post_id_is_non_empty_string(self, MockClient):
        """Verify a unique post ID is included in the INSERT (not blank)."""
        mock_client = MagicMock()
        mock_job    = MagicMock()
        mock_client.query.return_value = mock_job
        MockClient.return_value        = mock_client

        create_shared_post('user1', 'Hello world')

        executed_query = mock_client.query.call_args[0][0]
        # The UUID should appear in the VALUES clause
        self.assertRegex(executed_query,
                         r'[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}')


#----------------------------------------------
# Testing Streak
#----------------------------------------------
class TestStreakLogic(unittest.TestCase):

    @patch('data_fetcher.bigquery.Client')
    @patch('data_fetcher.datetime.date', wraps=datetime.date)
    def test_streak_increments_on_consecutive_day(self, mock_date, MockClient):
        """Scenario B: Logging a workout on a consecutive day should increment the streak."""
        today = datetime.date(2026, 4, 10)
        yesterday = datetime.date(2026, 4, 9)
        mock_date.today.return_value = today
        
        row = MagicMock()
        row.last_activity_date = yesterday
        row.current_streak = 5
        row.longest_streak = 10
        
        # Logic performs 2 queries: 1. SELECT, 2. UPDATE
        mock_client = _make_bq_client_mock([[row], []])
        MockClient.return_value = mock_client

        update_streak('user_123')
        
        # Verify call_args_list[1] is the UPDATE query
        update_call_args = mock_client.query.call_args_list[1][0][0]
        self.assertIn("SET current_streak = 6", update_call_args)

    @patch('data_fetcher.bigquery.Client')
    @patch('data_fetcher.datetime.date', wraps=datetime.date)
    def test_streak_resets_after_missing_a_day(self, mock_date, MockClient):
        """Scenario C: Logging a workout after a gap of 2+ days should reset streak to 1."""
        today = datetime.date(2026, 4, 10)
        three_days_ago = datetime.date(2026, 4, 7)
        mock_date.today.return_value = today
        
        row = MagicMock()
        row.last_activity_date = three_days_ago
        row.current_streak = 5
        row.longest_streak = 10
        
        mock_client = _make_bq_client_mock([[row], []])
        MockClient.return_value = mock_client

        update_streak('user_123')
        
        update_call_args = mock_client.query.call_args_list[1][0][0]
        self.assertIn("SET current_streak = 1", update_call_args)

    @patch('data_fetcher.bigquery.Client')
    @patch('data_fetcher.datetime.date', wraps=datetime.date)
    def test_get_streak_death_check(self, mock_date, MockClient):
        """Verify get_streak returns 0 if more than 1 day has passed since last activity."""
        today = datetime.date(2026, 4, 10)
        two_days_ago = datetime.date(2026, 4, 8) 
        mock_date.today.return_value = today
        
        row = MagicMock()
        row.last_activity_date = two_days_ago
        row.current_streak = 15
        row.longest_streak = 20
        
        MockClient.return_value = _make_bq_client_mock([[row]])

        result = get_streak('user_123')
        
        # (10th - 8th) = 2. current_streak becomes 0.
        self.assertEqual(result['current_streak'], 0)

if __name__ == '__main__':
    unittest.main()
