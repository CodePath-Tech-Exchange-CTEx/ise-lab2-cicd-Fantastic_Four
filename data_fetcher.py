#############################################################################
# data_fetcher.py
#
# This file contains functions to fetch data needed for the app.
#
# You will re-write these functions in Unit 3, and are welcome to alter the
# data returned in the meantime. We will replace this file with other data when
# testing earlier units.
#############################################################################

import datetime
import random
# connection with bigquery (had to run: pip install google-cloud-bigquery)
from google.cloud import bigquery 

# imports for VertexAI
import vertexai
from vertexai.generative_models import GenerativeModel

users = {
    'user1': {
        'full_name': 'Remi',
        'username': 'remi_the_rems',
        'date_of_birth': '1990-01-01',
        'profile_image': 'https://upload.wikimedia.org/wikipedia/commons/c/c8/Puma_shoes.jpg',
        'friends': ['user2', 'user3', 'user4'],
    },
    'user2': {
        'full_name': 'Blake',
        'username': 'blake',
        'date_of_birth': '1990-01-01',
        'profile_image': 'https://upload.wikimedia.org/wikipedia/commons/c/c8/Puma_shoes.jpg',
        'friends': ['user1'],
    },
    'user3': {
        'full_name': 'Jordan',
        'username': 'jordanjordanjordan',
        'date_of_birth': '1990-01-01',
        'profile_image': 'https://upload.wikimedia.org/wikipedia/commons/c/c8/Puma_shoes.jpg',
        'friends': ['user1', 'user4'],
    },
    'user4': {
        'full_name': 'Gemmy',
        'username': 'gems',
        'date_of_birth': '1990-01-01',
        'profile_image': 'https://upload.wikimedia.org/wikipedia/commons/c/c8/Puma_shoes.jpg',
        'friends': ['user1', 'user3'],
    },
}

# new get_user_sensor_data() function

def get_user_sensor_data(user_id, workout_id):
    """Returns a list of timestampped information for a given workout.

    This function currently returns random data. You will re-write it in Unit 3.
    """

    client = bigquery.Client()
    
    # 1. The SQL Query
    query = f"SELECT * FROM kevin-beltran-pena-uprm.ISE.SensorData  WHERE UserId = '{user_id}' AND WorkoutID = '{workout_id}'"
    
    # 2. Run the Query
    query_job = client.query(query)
    sensorData_results = query_job.result()
    
    # 3. Create the empty list
    sensorData_list = []
    
    # 4. Loop through the results using your exact code
    for row in sensorData_results:
        sensorData = {}
        sensorData["SensorId"] = row.SensorId
        sensorData["WorkoutID"] = row.WorkoutID
        sensorData["Timestamp"] = row.Timestamp
        sensorData["SensorValue"] = row.SensorValue
        
        sensorData_list.append(sensorData)

    # 5. Return the final list of dictionaries!
    return sensorData_list

# old get_user_sensor_data() function
# V V V V V V V V V V V V V V V V V
"""
def get_user_sensor_data(user_id, workout_id):
    
    sensor_data = []
    sensor_types = [
        'accelerometer',
        'gyroscope',
        'pressure',
        'temperature',
        'heart_rate',
    ]
    for index in range(random.randint(5, 100)):
        random_minute = str(random.randint(0, 59))
        if len(random_minute) == 1:
            random_minute = '0' + random_minute
        timestamp = '2024-01-01 00:' + random_minute + ':00'
        data = random.random() * 100
        sensor_type = random.choice(sensor_types)
        sensor_data.append(
            {'sensor_type': sensor_type, 'timestamp': timestamp, 'data': data}
        )
    return sensor_data
"""
# new get_user_workouts function

def get_user_workouts(user_id):
    """Returns a list of user's workouts.

    This function currently returns random data. You will re-write it in Unit 3.
    """
    client = bigquery.Client()
    
    # 1. The SQL Query
    query = f"SELECT * FROM kevin-beltran-pena-uprm.ISE.Workouts WHERE UserId = '{user_id}'"
    
    # 2. Run the Query
    query_job = client.query(query)
    workout_results = query_job.result()
    
    # 3. Create the empty list
    workouts_list = []
    
    # 4. Loop through the results using your exact code
    for row in workout_results:
        workouts = {}
        workouts["workout_id"] = row.WorkoutId
        workouts["start_timestamp"] = row.StartTimestamp
        workouts["distance"] = row.TotalDistance
        workouts["steps"] = row.TotalSteps
        workouts["calories_burned"] = row.CaloriesBurned
        # ADD MORE DATA
        
        workouts_list.append(workouts)
        
    # 5. Return the final list of dictionaries!
    return workouts_list


# old get_user_workouts function
# V V V V V V V V V V V V V V V
"""
def get_user_workouts(user_id):
    
    workouts = []
    for index in range(random.randint(1, 3)):
        random_lat_lng_1 = (
            1 + random.randint(0, 100) / 100,
            4 + random.randint(0, 100) / 100,
        )
        random_lat_lng_2 = (
            1 + random.randint(0, 100) / 100,
            4 + random.randint(0, 100) / 100,
        )
        workouts.append({
            'workout_id': f'workout{index}',
            'start_timestamp': '2024-01-01 00:00:00',
            'end_timestamp': '2024-01-01 00:30:00',
            'start_lat_lng': random_lat_lng_1,
            'end_lat_lng': random_lat_lng_2,
            'distance': random.randint(0, 200) / 10.0,
            'steps': random.randint(0, 20000),
            'calories_burned': random.randint(0, 100),
        })
    return workouts
"""

# new get_user_profile function

def get_user_profile(user_id):
    # Create a "messenger" client
    client = bigquery.Client()
    
    # SQL querys as a string
    query_for_users = f"SELECT * FROM kevin-beltran-pena-uprm.ISE.Users WHERE UserId = '{user_id}'"
    query_for_friends = f"SELECT UserId2 FROM kevin-beltran-pena-uprm.ISE.Friends WHERE UserId1 = '{user_id}'"
    
    # Send the query to BigQuery and wait for the job to finish
    query_job_users = client.query(query_for_users)
    query_job_friends = client.query(query_for_friends)
    
    
    # Get the results back (this returns an iterator of rows)
    user_results = query_job_users.result()

    users_disctionary = {}
    for row in user_results:
        users_disctionary["full_name"] = row.Name
        users_disctionary["username"] = row.Username
        users_disctionary["date_of_birth"] = row.DateOfBirth
        users_disctionary["profile_image"] = row.ImageUrl
        users_disctionary["friends"] = []
        
        for friend_row in query_job_friends.result():
            users_disctionary["friends"].append(friend_row.UserId2)
    
    
    # return the dictionary
    return users_disctionary


# old function to be delated
# v v v v v v v v v v v v v 
"""
def get_user_profile(user_id):
    #Returns information about the given user.

    #This function currently returns random data. You will re-write it in Unit 3.
    
    if user_id not in users:
        raise ValueError(f'User {user_id} not found.')
    return users[user_id]
"""
# ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ 


# new get_user_posts function

def get_user_posts(user_id):
    
    client = bigquery.Client()
    
    # 1. The Fixed SQL Query (Using AuthorId)
    query = f"SELECT * FROM kevin-beltran-pena-uprm.ISE.Posts WHERE AuthorId = '{user_id}'"
    
    # 2. Run the Query
    query_job = client.query(query)
    posts_results = query_job.result()
    
    # 3. NEW STEP: Grab the user's profile so we have their username and picture!
    user_profile = get_user_profile(user_id)
    
    # 4. Create the empty list
    posts_list = []
    
    # 5. Loop through the results
    for row in posts_results:
        post = {}
        
        # Pulling the missing info from the profile we just grabbed:
        post["username"] = user_profile["username"] 
        post["user_image"] = user_profile["profile_image"] 
        
        # Pulling the rest of the info from the BigQuery row:
        post["timestamp"] = row.Timestamp
        post["content"] = row.Content
        post["post_image"] = row.ImageUrl # Your table calls it ImageUrl!
        
        posts_list.append(post)
        
    # 6. Return the final list of dictionaries!
    return posts_list


"""

# old function to be delated
# v v v v v v v v v v v v v 
def get_user_posts(user_id):
    
    content = random.choice([
        'Had a great workout today!',
        'The AI really motivated me to push myself further, I ran 10 miles!',
    ])

    user_profile = users[user_id]

    return [{
        'username': user_profile['username'],
        'user_image': user_profile['profile_image'],
        'timestamp': '2024-01-01 00:00:00',
        'content': content,
        'post_image': 'https://picsum.photos/600/400',
    }]

"""


# new get_genai_advice function
def get_genai_advice(user_id):

    # 1. Initialize the connection to your project
    # Note: 'us-central1' is the standard location for Vertex AI
    vertexai.init(project="kevin-beltran-pena-uprm", location="us-central1")
    
    # 2. Pick the brain you want to use (Gemini Flash is fast and great for this)
    model = GenerativeModel("gemini-2.5-flash-lite")
    
    # 3. Give the AI instructions (the "prompt")
    prompt = "Write a 1-sentence motivational fitness message for someone tracking their workouts."
    
    # 4. Ask the AI to generate the response
    ai_response = model.generate_content(prompt)
    
    # 5. Extract just the text from the response
    generated_text = ai_response.text
    
    # 6. Build the dictionary that modules.py expects
    return {
        'advice_id': 'ai_advice_1',
        'timestamp': str(datetime.datetime.now()), # Stamps it with the current time
        'content': generated_text,
        'image': None # We can leave the image blank for now!
    }


"""
# old function to be delated
# v v v v v v v v v v v v v 
def get_genai_advice(user_id):
    
    advice = random.choice([
        'Your heart rate indicates you can push yourself further. You got this!',
        "You're doing great! Keep up the good work.",
        'You worked hard yesterday, take it easy today.',
        'You have burned 100 calories so far today!',
    ])
    image = random.choice([
        'https://plus.unsplash.com/premium_photo-1669048780129-051d670fa2d1?q=80&w=3870&auto=format&fit=crop&ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D',
        None,
    ])
    return {
        'advice_id': 'advice1',
        'timestamp': '2024-01-01 00:00:00',
        'content': advice,
        'image': image,
    }
"""