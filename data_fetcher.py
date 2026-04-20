#############################################################################
# data_fetcher.py
#
# This file contains functions to fetch data needed for the app.
#############################################################################

import datetime
import random
import uuid

from zoneinfo import ZoneInfo

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
    """Returns a list of the user's workouts matching the updated BigQuery schema.

    Input:  user_id
    Output: list of dicts with keys workout_id, workout_type, start_timestamp,
            end_timestamp, distance, steps, calories_burned, total_time, hr_avg, hr_peak
    """
    from google.cloud import bigquery
    client = bigquery.Client()

    # Updated query
    query = f"""
        SELECT
            WorkoutId,
            WorkoutType,
            StartTimestamp,
            EndTimestamp,
            TotalDistance,
            TotalSteps,
            CaloriesBurned,
            TotalTimeMinutes,
            HeartRateAvg,
            HeartRatePeak
        FROM {_table('Workouts')}
        WHERE UserId = '{user_id}'
        ORDER BY StartTimestamp DESC
    """

    query_job = client.query(query)
    results = query_job.result()

    workouts_list = []
    for row in results:

        workouts_list.append({
            "workout_id":       row.WorkoutId,
            "workout_type":     row.WorkoutType if hasattr(row, 'WorkoutType') else "Unknown",
            "start_timestamp":  row.StartTimestamp,
            "end_timestamp":    row.EndTimestamp,
            "distance":         row.TotalDistance,
            "steps":            row.TotalSteps,
            "calories_burned":  row.CaloriesBurned,
            "total_time":       row.TotalTimeMinutes if hasattr(row, 'TotalTimeMinutes') else 0,
            "hr_avg":           row.HeartRateAvg if hasattr(row, 'HeartRateAvg') else 0,
            "hr_peak":          row.HeartRatePeak if hasattr(row, 'HeartRatePeak') else 0,
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
    Takes data from the dynamic Streamlit form and pushes it to BigQuery.
    Handles the Workouts table, and optionally the GymExercises table.
    """
    
    
    client = bigquery.Client()

    #Setup Time and IDs
    workout_id = str(uuid.uuid4())
    miami_tz = ZoneInfo("America/New_York")
    today = datetime.datetime.now(miami_tz).date()

    # Combine the Streamlit time objects with today's date for BigQuery
    start_dt = datetime.datetime.combine(today, workout_data["start_time"])
    end_dt = datetime.datetime.combine(today, workout_data["end_time"])
    
    start_ts = start_dt.strftime("%Y-%m-%d %H:%M:%S")
    end_ts = end_dt.strftime("%Y-%m-%d %H:%M:%S")

    # Extract shared data (using .get() safely falls back to 0 if missing)
    total_time = workout_data.get("total_time", 0)
    calories = workout_data.get("calories", 0)
    hr_avg = workout_data.get("hr", 0)
    hr_peak = workout_data.get("hr_peak", 0)

    # Handle specific workout logic
    if workout_type in ["Running", "Swimming"]:
        distance = workout_data.get("miles", 0)
    else:
        distance = 0.0 # Gym doesn't track distance

    # Push to the main Workouts table
    workout_query = f"""
        INSERT INTO {_table('Workouts')} 
        (WorkoutId, UserId, WorkoutType, StartTimestamp, EndTimestamp, TotalDistance, CaloriesBurned, TotalTimeMinutes, HeartRateAvg, HeartRatePeak, TotalSteps) 
        VALUES 
        ('{workout_id}', '{user_id}', '{workout_type}', '{start_ts}', '{end_ts}', {distance}, {calories}, {total_time}, {hr_avg}, {hr_peak}, 0)
    """
    client.query(workout_query).result()

    # Push to the GymExercises table (if it's a Gym workout)
    if workout_type == "Gym" and "exercises" in workout_data:
        exercises = workout_data["exercises"]
        
        if exercises:
            value_strings = []
            for ex in exercises:
                ex_id = str(uuid.uuid4())
                # Replace apostrophes to prevent SQL crashes (e.g., "Lat Pulldown's")
                safe_name = ex['name'].replace("'", "\\'") 
                
                # Format a single row of values
                val = f"('{ex_id}', '{workout_id}', '{safe_name}', {ex['sets']}, {ex['reps']}, {ex['weight']})"
                value_strings.append(val)
            
            # Combine all rows into one giant INSERT query
            gym_query = f"""
                INSERT INTO {_table('GymExercises')} 
                (ExerciseId, WorkoutId, ExerciseName, Sets, Reps, Weight)
                VALUES {', '.join(value_strings)}
            """
            client.query(gym_query).result()

    # Update the user's streak
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
