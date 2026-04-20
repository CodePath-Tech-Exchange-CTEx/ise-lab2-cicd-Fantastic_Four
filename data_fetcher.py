#############################################################################
# data_fetcher.py
#
# This file contains functions to fetch data needed for the app.
#############################################################################

import datetime
import random
import uuid

from zoneinfo import ZoneInfo # can change the time zone (not used yet)

from google.cloud import bigquery

import vertexai
from vertexai.generative_models import GenerativeModel

# ---------------------------------------------------------------------------
# Configuration — swap these two values for your team's project
# ---------------------------------------------------------------------------
GCP_PROJECT_ID = "kevin-beltran-pena-uprm"
DATASET = "ISE"
# ---------------------------------------------------------------------------


def _table(name):
    """Helper that returns a fully-qualified BigQuery table reference."""
    return f"`{GCP_PROJECT_ID}.{DATASET}.{name}`"


# ===========================================================================
# READ functions
# ===========================================================================

def get_user_workouts(user_id):
    """Returns a list of the user's workouts.

    Input:  user_id
    Output: list of dicts with keys workout_id, start_timestamp,
            end_timestamp, start_lat_lng, end_lat_lng,
            distance, steps, calories_burned
    """
    client = bigquery.Client()

    query = f"""
        SELECT
            WorkoutId,
            StartTimestamp,
            EndTimestamp,
            StartLocationLat,
            StartLocationLong,
            EndLocationLat,
            EndLocationLong,
            TotalDistance,
            TotalSteps,
            CaloriesBurned
        FROM {_table('Workouts')}
        WHERE UserId = '{user_id}'
        ORDER BY StartTimestamp DESC
    """

    query_job = client.query(query)
    results = query_job.result()

    workouts_list = []
    for row in results:
        start_lat_lng = (
            (row.StartLocationLat, row.StartLocationLong)
            if row.StartLocationLat is not None and row.StartLocationLong is not None
            else None
        )
        end_lat_lng = (
            (row.EndLocationLat, row.EndLocationLong)
            if row.EndLocationLat is not None and row.EndLocationLong is not None
            else None
        )

        workouts_list.append({
            "workout_id":       row.WorkoutId,
            "start_timestamp":  row.StartTimestamp,
            "end_timestamp":    row.EndTimestamp,
            "start_lat_lng":    start_lat_lng,
            "end_lat_lng":      end_lat_lng,
            "distance":         row.TotalDistance,
            "steps":            row.TotalSteps,
            "calories_burned":  row.CaloriesBurned,
        })

    return workouts_list


def get_user_profile(user_id):
    """Returns profile information for the given user.

    Input:  user_id
    Output: dict with keys full_name, username, date_of_birth,
            profile_image, friends (list of friend user_ids)
    """
    client = bigquery.Client()

    query_for_user = f"""
        SELECT UserId, Name, Username, ImageUrl, DateOfBirth
        FROM {_table('Users')}
        WHERE UserId = '{user_id}'
    """
    query_for_friends = f"""
        SELECT UserId2 FROM {_table('Friends')} WHERE UserId1 = '{user_id}'
        UNION DISTINCT
        SELECT UserId1 FROM {_table('Friends')} WHERE UserId2 = '{user_id}'
    """

    user_job    = client.query(query_for_user)
    friends_job = client.query(query_for_friends)

    friends_list = [row.UserId2 if hasattr(row, 'UserId2') else row[0]
                    for row in friends_job.result()]

    profile = {}
    for row in user_job.result():
        profile = {
            "full_name":     row.Name,
            "username":      row.Username,
            "date_of_birth": row.DateOfBirth,
            "profile_image": row.ImageUrl,
            "friends":       friends_list,
        }

    return profile


def get_user_posts(user_id):
    """Returns a list of posts authored by the given user.

    Input:  user_id
    Output: list of dicts with keys user_id, post_id, username,
            user_image, timestamp, content, post_image
    """
    client = bigquery.Client()

    query = f"""
        SELECT PostId, AuthorId, Timestamp, ImageUrl, Content
        FROM {_table('Posts')}
        WHERE AuthorId = '{user_id}'
        ORDER BY Timestamp DESC
    """

    query_job = client.query(query)
    posts_results = query_job.result()

    user_profile = get_user_profile(user_id)

    posts_list = []
    for row in posts_results:
        posts_list.append({
            "user_id":    user_id,
            "post_id":    row.PostId,
            "username":   user_profile.get("username", ""),
            "user_image": user_profile.get("profile_image", ""),
            "timestamp":  row.Timestamp,
            "content":    row.Content,
            "post_image": row.ImageUrl,
        })

    return posts_list


def get_genai_advice(user_id):
    """Returns one piece of AI-generated fitness advice personalised to the user.

    Images are included ~30 % of the time (as required by the spec).

    Input:  user_id
    Output: dict with keys advice_id, timestamp, content, image
    """
    vertexai.init(project=GCP_PROJECT_ID, location="us-central1")
    model = GenerativeModel("gemini-2.5-flash-lite")

    try:
        profile  = get_user_profile(user_id)
        workouts = get_user_workouts(user_id)

        recent_steps    = workouts[0]["steps"]          if workouts else "unknown"
        recent_calories = workouts[0]["calories_burned"] if workouts else "unknown"
        username        = profile.get("full_name", "athlete")

        prompt = (
            f"You are a supportive fitness coach. Write exactly one short, "
            f"motivational sentence for {username}, who recently logged "
            f"{recent_steps} steps and burned {recent_calories} calories. "
            f"Be encouraging and specific."
        )
    except Exception:
        prompt = (
            "Write exactly one short, motivational sentence for someone "
            "who is actively tracking their workouts."
        )

    ai_response    = model.generate_content(prompt)
    generated_text = ai_response.text.strip()

    image_options = [
        "https://images.unsplash.com/photo-1517836357463-d25dfeac3438?w=800",
        "https://images.unsplash.com/photo-1534438327276-14e5300c3a48?w=800",
        "https://images.unsplash.com/photo-1571019613454-1cb2f99b2d8b?w=800",
    ]
    chosen_image = random.choice(image_options) if random.random() < 0.30 else None

    return {
        "advice_id": str(uuid.uuid4()),
        "timestamp": str(datetime.datetime.now()),
        "content":   generated_text,
        "image":     chosen_image,
    }


def get_streak(user_id):
    """Returns the current streak for the given user.

    Performs a midnight check: if more than 1 day has passed since the last
    activity with no workout logged, the streak is treated as 0 in the UI.

    Input:  user_id
    Output: dict with keys current_streak, last_activity_date
    """
    client = bigquery.Client()

    query = f"""
        SELECT current_streak, last_activity_date
        FROM {_table('Users')}
        WHERE UserId = '{user_id}'
    """
    results = list(client.query(query).result())

    if not results:
        return {"current_streak": 0, "last_activity_date": None}

    row     = results[0]
    today   = datetime.date.today()
    last    = row.last_activity_date
    current = row.current_streak or 0

    # Midnight check: more than 1 day since last activity means streak is dead
    if last and (today - last).days > 1:
        current = 0

    return {
        "current_streak":     current,
        "last_activity_date": last,
    }

def verify_login(Username, passowrd):
    """
    credentials check
    """
    client = bigquery.Client()

    query = f"""
        SELECT UserID 
        FROM {_table('Users')}
        WHERE Username = '{Username}' AND Password = '{passowrd}'
    """

    query_job = client.query(query)
    results = list(query_job.result())

    if results == []:
        return None
    else:
        return results[0].UserID


def get_user_workout_dates(user_id):
    """Returns a simple list of workout date strings for the calendar."""
    # Re-use our existing function to get the data
    user_workouts = get_user_workouts(user_id)
    
    workout_dates = []
    for workout in user_workouts:
        date_only = str(workout['start_timestamp'])[:10]
        workout_dates.append(date_only)
        
    return workout_dates

# ===========================================================================
# WRITE functions
# ===========================================================================

def create_shared_post(user_id, content):
    """Inserts a new post into the BigQuery Posts table.

    Input:  user_id, content (string)
    Output: None (raises on failure)
    """
    client = bigquery.Client()

    post_id      = str(uuid.uuid4())
    current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    safe_content = content.replace("'", "\\'")

    query = f"""
        INSERT INTO {_table('Posts')} (PostId, AuthorId, Timestamp, ImageUrl, Content)
        VALUES ('{post_id}', '{user_id}', '{current_time}', NULL, '{safe_content}')
    """

    query_job = client.query(query)
    query_job.result()


def create_user(Name, Username, Password, DateOfBirth, ImageUrl):
    """
    Inserts a new user into the BigQuery Users table.

    Input:  Name, Username, Password, DateOfBirth, ImageUrl
    Output: None
    """
    client = bigquery.Client()

    UserId = str(uuid.uuid4())

    query = f"""
    INSERT INTO {_table('Users')} (UserId, Name, Username, Password, DateOfBirth, ImageUrl)
    VALUES ('{UserId}', '{Name}', '{Username}', '{Password}', '{DateOfBirth}', '{ImageUrl}')
    """

    query_job = client.query(query)
    query_job.result()



def add_new_workout(user_id, workout_type, workout_data):
    """
    this function gets the data from add_workot_page.py and push them into the Workouts table

    SO FAR, IT IS JUST A TEST: it returns just few data to see if the app works

    TO DO:
    - update the database, to accept the right data
    - return the right data from this function
    """
    
    # We generate a unique ID and get the current time for the database
    import uuid
    import datetime
    workout_id = str(uuid.uuid4())
    current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    if workout_type == "Running":
        distance = workout_data["miles"]
        calories = workout_data["calories"]
        # ... (extract the rest)

        # pass more data
        # we have to assign values to TotalSteps and StartTimestam. if not, module.py crushes
        query = f"""
        INSERT INTO {_table('Workouts')} (WorkoutId, UserId, TotalDistance, CaloriesBurned, TotalSteps, StartTimestamp) 
        VALUES ('{workout_id}', '{user_id}', {distance}, {calories}, 0, '{current_time}')
        """

    elif workout_type == "Swimming":
        distance = workout_data["miles"]
        calories = workout_data["calories"]
        # ... (extract the rest)

        # pass more data
        query = f"""
        INSERT INTO {_table('Workouts')} (WorkoutId, UserId, TotalDistance, CaloriesBurned, TotalSteps, StartTimestamp) 
        VALUES ('{workout_id}', '{user_id}', {distance}, {calories}, 0, '{current_time}')
        """

    elif workout_type == "Gym":
        distance = 0 # gym doeas't have distance variables
        calories = workout_data["calories"]
        # ... (extract the rest)

        # pass more data 
        query = f"""
        INSERT INTO {_table('Workouts')} (WorkoutId, UserId, TotalDistance, CaloriesBurned, TotalSteps, StartTimestamp) 
        VALUES ('{workout_id}', '{user_id}', {distance}, {calories}, 0, '{current_time}')
        """
    
    client = bigquery.Client()
    
    query_job = client.query(query)
    query_job.result()

    update_streak(user_id)

def update_streak(user_id):
    client = bigquery.Client()

    query = f"""
        SELECT current_streak, longest_streak, last_activity_date
        FROM {_table('Users')}
        WHERE UserId = '{user_id}'
    """
    results = list(client.query(query).result())

    if not results:
        return

    row     = results[0]
    today   = datetime.date.today()
    last    = row.last_activity_date
    current = row.current_streak or 0
    longest = row.longest_streak or 0

    # Scenario A: already worked out today, do nothing
    if last == today:
        return

    # Scenario B: next day, increment streak
    elif last == today - datetime.timedelta(days=1):
        current += 1

    # Scenario C: missed a day or first ever workout, reset to 1
    else:
        current = 1

    longest = max(current, longest)

    update_query = f"""
        UPDATE {_table('Users')}
        SET current_streak = {current},
            longest_streak = {longest},
            last_activity_date = '{today}'
        WHERE UserId = '{user_id}'
    """
    client.query(update_query).result()
