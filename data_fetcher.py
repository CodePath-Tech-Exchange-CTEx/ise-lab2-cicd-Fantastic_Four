#############################################################################
# data_fetcher.py
#
# This file handles all backend database operations (Google BigQuery) 
# and GenAI API calls (Vertex AI) for the SDS Fitness app.
#############################################################################

import datetime
import uuid
import json
import random
from zoneinfo import ZoneInfo

# GCP & AI Imports
from google.cloud import bigquery
import vertexai
from vertexai.generative_models import GenerativeModel

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------
GCP_PROJECT_ID = "kevin-beltran-pena-uprm"
DATASET = "ISE"

def _table(name):
    """Helper that returns a fully-qualified BigQuery table reference."""
    return f"`{GCP_PROJECT_ID}.{DATASET}.{name}`"


# ===========================================================================
# 1. USER & AUTHENTICATION
# ===========================================================================

def verify_login(username, password):
    """Verifies user credentials against the database and returns the UserID if valid."""
    client = bigquery.Client()

    query = f"""
        SELECT UserID 
        FROM {_table('Users')}
        WHERE Username = '{username}' AND Password = '{password}'
    """
    results = list(client.query(query).result())

    if not results:
        return None
    else:
        return results[0].UserID


def create_user(name, username, password, date_of_birth, image_url):
    """Inserts a new user record into the BigQuery Users table."""
    client = bigquery.Client()
    user_id = str(uuid.uuid4())

    query = f"""
    INSERT INTO {_table('Users')} (UserId, Name, Username, Password, DateOfBirth, ImageUrl)
    VALUES ('{user_id}', '{name}', '{username}', '{password}', '{date_of_birth}', '{image_url}')
    """
    client.query(query).result()


def get_user_profile(user_id):
    """Returns profile information and a list of friends for the given user."""
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

    user_job = client.query(query_for_user)
    friends_job = client.query(query_for_friends)

    # Collect friends first (single pass to avoid re-iteration issues)
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


# ===========================================================================
# 2. WORKOUTS (READ/WRITE/DELETE)
# ===========================================================================

def add_new_workout(user_id, workout_type, workout_data):
    """
    Takes data from the Streamlit UI form and pushes it to BigQuery.
    Handles the Workouts table, and optionally the GymExercises relational table.
    """
    client = bigquery.Client()

    distance = 0.0
    avg_speed = 0.0
    elevation_gain = 0
    difficulty = "N/A"

    # Setup Time and IDs
    workout_id = str(uuid.uuid4())
    miami_tz = ZoneInfo("America/New_York")
    today = datetime.datetime.now(miami_tz).date()

    start_dt = datetime.datetime.combine(today, workout_data["start_time"])
    end_dt = datetime.datetime.combine(today, workout_data["end_time"])
    
    start_ts = start_dt.strftime("%Y-%m-%d %H:%M:%S")
    end_ts = end_dt.strftime("%Y-%m-%d %H:%M:%S")

    # Extract shared data
    total_time = workout_data.get("total_time", 0)
    calories = workout_data.get("calories", 0)
    hr_avg = workout_data.get("hr", 0)
    hr_peak = workout_data.get("hr_peak", 0)

    # Handle specific workout logic
    if workout_type in ["Running", "Swimming"]:
        distance = workout_data.get("miles", 0)
    elif workout_type == "Cycling":
        distance = workout_data.get("miles", 0.0)
        avg_speed = workout_data.get("avg_speed", 0.0)
    elif workout_type == "Hiking":
        distance = workout_data.get("miles", 0.0)
        elevation_gain = workout_data.get("elevation_gain", 0)
        difficulty = workout_data.get("difficulty", "Moderate")
    else:
        distance = 0.0 # Gym doesn't track distance
    
    # Push standard workout data
    workout_query = f"""
        INSERT INTO {_table('Workouts')} 
        (WorkoutId, UserId, WorkoutType, StartTimestamp, EndTimestamp, TotalDistance, CaloriesBurned, 
         TotalTimeMinutes, HeartRateAvg, HeartRatePeak, TotalSteps, AvgSpeed, ElevationGain, Difficulty) 
        VALUES 
        ('{workout_id}', '{user_id}', '{workout_type}', '{start_ts}', '{end_ts}', {distance}, {calories}, 
         {total_time}, {hr_avg}, {hr_peak}, 0, {avg_speed}, {elevation_gain}, '{difficulty}')
    """
    client.query(workout_query).result()

    # Push to the GymExercises table if applicable
    if workout_type == "Gym" and "exercises" in workout_data:
        exercises = workout_data["exercises"]
        if exercises:
            value_strings = []
            for ex in exercises:
                ex_id = str(uuid.uuid4())
                safe_name = ex['name'].replace("'", "\\'") 
                val = f"('{ex_id}', '{workout_id}', '{safe_name}', {ex['sets']}, {ex['reps']}, {ex['weight']})"
                value_strings.append(val)
            
            gym_query = f"""
                INSERT INTO {_table('GymExercises')} 
                (ExerciseId, WorkoutId, ExerciseName, Sets, Reps, Weight)
                VALUES {', '.join(value_strings)}
            """
            client.query(gym_query).result()

    update_streak(user_id)


def get_user_workouts(user_id):
    """Returns a list of all historical workouts for a specific user."""
    client = bigquery.Client()

    query = f"""
        SELECT
            WorkoutId, WorkoutType, StartTimestamp, EndTimestamp, TotalDistance,
            TotalSteps, CaloriesBurned, TotalTimeMinutes, HeartRateAvg, HeartRatePeak
        FROM {_table('Workouts')}
        WHERE UserId = '{user_id}'
        ORDER BY StartTimestamp DESC
    """
    results = client.query(query).result()

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


def delete_workout(workout_id):
    """Deletes a specific workout from BigQuery using its ID."""
    client = bigquery.Client()
    query = f"DELETE FROM {_table('Workouts')} WHERE WorkoutId = '{workout_id}'"
    client.query(query).result()


# ===========================================================================
# 3. CALENDAR & SCHEDULING
# ===========================================================================

def get_user_workout_dates(user_id):
    """Returns a simple list of YYYY-MM-DD date strings for completed workouts."""
    user_workouts = get_user_workouts(user_id)
    
    workout_dates = []
    for workout in user_workouts:
        date_only = str(workout['start_timestamp'])[:10]
        workout_dates.append(date_only)
        
    return workout_dates


def get_all_calendar_events(user_id):
    """Fetches all workouts (past and scheduled) and formats them for the Streamlit Calendar."""
    client = bigquery.Client()
    
    query = f"""
        SELECT WorkoutId, WorkoutType, StartTimestamp, TotalTimeMinutes, IsScheduled
        FROM {_table('Workouts')}
        WHERE UserId = '{user_id}'
    """
    results = client.query(query).result()
    
    events = []
    for row in results:
        is_scheduled = row.IsScheduled if hasattr(row, 'IsScheduled') else False
        
        # Color Coding Logic
        if is_scheduled:
            bg_color, border_color, text_color, icon = "#E0E7FF", "#6366F1", "#3730A3", "⏱️"
        else:
            bg_color, border_color, text_color, icon = "#DCFCE7", "#22C55E", "#166534", "✅"
            
        time_mins = row.TotalTimeMinutes if hasattr(row, 'TotalTimeMinutes') and row.TotalTimeMinutes else 0
        raw_type = row.WorkoutType if hasattr(row, 'WorkoutType') and row.WorkoutType is not None else "Workout"
        workout_name = raw_type.replace(" (AI Suggestion)", "") 
        
        events.append({
            "title": f"{icon} {workout_name} ({time_mins}m)",
            "start": str(row.StartTimestamp),
            "backgroundColor": bg_color,
            "borderColor": border_color,
            "textColor": text_color,
            "display": "block" 
        })
        
    return events


def schedule_ai_workout(user_id, workout_type, future_date, total_time):
    """Saves a future AI-generated workout to the database."""
    client = bigquery.Client()
    
    workout_id = str(uuid.uuid4())
    scheduled_ts = f"{future_date} 12:00:00"
    
    query = f"""
        INSERT INTO {_table('Workouts')} 
        (WorkoutId, UserId, WorkoutType, StartTimestamp, EndTimestamp, TotalTimeMinutes, IsScheduled, TotalSteps) 
        VALUES 
        ('{workout_id}', '{user_id}', '{workout_type} (AI Suggestion)', '{scheduled_ts}', '{scheduled_ts}', {total_time}, TRUE, 0)
    """
    client.query(query).result()


def get_scheduled_workouts(user_id):
    """Fetches only future scheduled AI workouts for the user."""
    client = bigquery.Client()
    
    query = f"""
        SELECT WorkoutId, WorkoutType, StartTimestamp, TotalTimeMinutes
        FROM {_table('Workouts')}
        WHERE UserId = '{user_id}' AND IsScheduled = TRUE
        ORDER BY StartTimestamp ASC
    """
    return list(client.query(query).result())


# ===========================================================================
# 4. STREAKS & COMMUNITY FEED
# ===========================================================================

def get_streak(user_id):
    """Returns the current streak, applying a midnight reset if a day was skipped."""
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

    if last and (today - last).days > 1:
        current = 0

    return {"current_streak": current, "last_activity_date": last}


def update_streak(user_id):
    """Calculates and updates the user's current and longest streak upon logging activity."""
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

    if last == today:
        return
    elif last == today - datetime.timedelta(days=1):
        current += 1
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


def create_shared_post(user_id, content):
    """Inserts a new text post into the BigQuery Posts table."""
    client = bigquery.Client()

    post_id      = str(uuid.uuid4())
    current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    safe_content = content.replace("'", "\\'")

    query = f"""
        INSERT INTO {_table('Posts')} (PostId, AuthorId, Timestamp, ImageUrl, Content)
        VALUES ('{post_id}', '{user_id}', '{current_time}', NULL, '{safe_content}')
    """
    client.query(query).result()


def get_user_posts(user_id):
    """Returns a list of posts authored by the given user with their profile info attached."""
    client = bigquery.Client()

    query = f"""
        SELECT PostId, AuthorId, Timestamp, ImageUrl, Content
        FROM {_table('Posts')}
        WHERE AuthorId = '{user_id}'
        ORDER BY Timestamp DESC
    """
    posts_results = client.query(query).result()

    # Grab profile once to attach username/avatar to every post
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


# ===========================================================================
# 5. AI INTEGRATIONS (VERTEX AI)
# ===========================================================================

def get_genai_advice(user_id):
    """Generates one piece of personalized fitness advice using Gemini."""
    vertexai.init(project=GCP_PROJECT_ID, location="us-central1")
    model = GenerativeModel("gemini-2.5-flash-lite")

    try:
        profile  = get_user_profile(user_id)
        workouts = get_user_workouts(user_id)

        recent_steps    = workouts[0]["steps"] if workouts else "unknown"
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

    # 30% chance to include a motivational image per specifications
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


def generate_ai_workout_plan(user_id):
    """Uses Gemini to generate 5 distinct workout suggestions returned as JSON."""
    vertexai.init(project=GCP_PROJECT_ID, location="us-central1")
    
    # Using JSON mode ensures Python can easily parse the response into a list of dicts
    model = GenerativeModel(
        "gemini-2.5-flash-lite",
        generation_config={"response_mime_type": "application/json"}
    )
    
    profile = get_user_profile(user_id)
    username = profile.get("full_name", "athlete")

    prompt = f"""
    You are an elite fitness coach designing a plan for {username}. 
    Provide exactly 5 distinct workout suggestions, one for each of these sports: Running, Swimming, Gym, Hiking, and Cycling.
    Return the response as a JSON array containing 5 objects. 
    Each object must have these keys:
    - "title": A catchy title (string)
    - "workout_type": Must be "Running", "Swimming", "Gym", "Hiking", or "Cycling" (string)
    - "total_time": Estimated minutes (integer)
    - "description": A short, 1-sentence summary of the workout (string)
    """
    
    response = model.generate_content(prompt)
    try:
        return json.loads(response.text)
    except Exception:
        return []