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

# needed to generate random ID
import uuid 

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


# functions to read data

#----------------------------------------------------------------------------------------------------------------------------
#----------------------------------------------------------------------------------------------------------------------------

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

#----------------------------------------------------------------------------------------------------------------------------
#----------------------------------------------------------------------------------------------------------------------------

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

#----------------------------------------------------------------------------------------------------------------------------
#----------------------------------------------------------------------------------------------------------------------------

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

#----------------------------------------------------------------------------------------------------------------------------
#----------------------------------------------------------------------------------------------------------------------------

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

#----------------------------------------------------------------------------------------------------------------------------
#----------------------------------------------------------------------------------------------------------------------------

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

#----------------------------------------------------------------------------------------------------------------------------
#----------------------------------------------------------------------------------------------------------------------------

# functions to write data

#----------------------------------------------------------------------------------------------------------------------------
#----------------------------------------------------------------------------------------------------------------------------

# CREATE A UNIT TEST FOR THIS FUNCTION
def create_shared_post(user_id, content):
    """Inserts a new post into the BigQuery Posts table."""
    client = bigquery.Client()
    
    # Generate a random unique ID for the post and get the current time
    post_id = str(uuid.uuid4())
    current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    # 1. The SQL INSERT Query
    query = f"""
        INSERT INTO kevin-beltran-pena-uprm.ISE.Posts (PostId, AuthorId, Timestamp, ImageUrl, Content)
        VALUES ('{post_id}', '{user_id}', '{current_time}', NULL, '{content}')
    """
    
    # 2. Run the Query to save it to the database!
    query_job = client.query(query)
    query_job.result() # Wait for it to finish