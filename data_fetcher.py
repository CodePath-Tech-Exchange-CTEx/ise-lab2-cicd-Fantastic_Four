#############################################################################
# data_fetcher.py
#
# This file contains functions to fetch data needed for the app.
#############################################################################

import datetime
import random
import uuid

<<<<<<< unit3-data-fetcher-fix-amari
=======

import json
import random

from zoneinfo import ZoneInfo

>>>>>>> main
from google.cloud import bigquery

import vertexai
from vertexai.generative_models import GenerativeModel

# ---------------------------------------------------------------------------
# Configuration — swap these two values for your team's project
# ---------------------------------------------------------------------------
GCP_PROJECT_ID = "kevin-beltran-pena-uprm"
DATASET = "ISE"
# ---------------------------------------------------------------------------
<<<<<<< unit3-data-fetcher-fix-amari


def _table(name):
    """Helper that returns a fully-qualified BigQuery table reference."""
    return f"`{GCP_PROJECT_ID}.{DATASET}.{name}`"


# ===========================================================================
# READ functions
# ===========================================================================

def get_user_sensor_data(user_id, workout_id):
    """Returns a list of timestamped sensor readings for a given workout.

    The workout must belong to the given user_id (verified via a JOIN with
    the Workouts table, since SensorData has no UserId column of its own).

    Input:  user_id, workout_id
    Output: list of dicts with keys sensor_type, timestamp, data, units
    """
    client = bigquery.Client()

    query = f"""
        SELECT
            st.Name        AS sensor_type,
            sd.Timestamp   AS timestamp,
            sd.SensorValue AS data,
            st.Units       AS units
        FROM {_table('SensorData')} sd
        JOIN {_table('SensorTypes')} st
          ON sd.SensorId = st.SensorId
        JOIN {_table('Workouts')} w
          ON sd.WorkoutID = w.WorkoutId
        WHERE sd.WorkoutID = '{workout_id}'
          AND w.UserId     = '{user_id}'
        ORDER BY sd.Timestamp
    """

    query_job = client.query(query)
    results = query_job.result()

    sensor_list = []
    for row in results:
        sensor_list.append({
            "sensor_type": row.sensor_type,
            "timestamp":   row.timestamp,
            "data":        row.data,
            "units":       row.units,
        })

    return sensor_list


def get_user_workouts(user_id):
    """Returns a list of the user's workouts.

    Input:  user_id
    Output: list of dicts with keys workout_id, start_timestamp,
            end_timestamp, start_lat_lng, end_lat_lng,
            distance, steps, calories_burned
=======


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
>>>>>>> main
    """
    from google.cloud import bigquery
    client = bigquery.Client()

<<<<<<< unit3-data-fetcher-fix-amari
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
=======
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
>>>>>>> main
        FROM {_table('Workouts')}
        WHERE UserId = '{user_id}'
        ORDER BY StartTimestamp DESC
    """

    query_job = client.query(query)
    results = query_job.result()

    workouts_list = []
    for row in results:
<<<<<<< unit3-data-fetcher-fix-amari
        # Lat/lng pairs may be NULL in the database — guard gracefully
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

=======

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
>>>>>>> main

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

<<<<<<< unit3-data-fetcher-fix-amari
    # Collect friends first (single pass — avoids re-iteration issues)
=======
>>>>>>> main
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

<<<<<<< unit3-data-fetcher-fix-amari
    # Grab profile once so we have username / avatar for every post
=======
>>>>>>> main
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
<<<<<<< unit3-data-fetcher-fix-amari


def get_genai_advice(user_id):
    """Returns one piece of AI-generated fitness advice personalised to the user.

    Images are included ~30 % of the time (as required by the spec).

    Input:  user_id
    Output: dict with keys advice_id, timestamp, content, image
    """
    vertexai.init(project=GCP_PROJECT_ID, location="us-central1")
    model = GenerativeModel("gemini-2.5-flash-lite")

    # Pull some user context to make the advice personalised
    try:
        profile  = get_user_profile(user_id)
        workouts = get_user_workouts(user_id)

        recent_steps    = workouts[0]["steps"]    if workouts else "unknown"
        recent_calories = workouts[0]["calories_burned"] if workouts else "unknown"
        username        = profile.get("full_name", "athlete")

        prompt = (
            f"You are a supportive fitness coach. Write exactly one short, "
            f"motivational sentence for {username}, who recently logged "
            f"{recent_steps} steps and burned {recent_calories} calories. "
            f"Be encouraging and specific."
        )
    except Exception:
        # Fallback prompt if data fetching fails
        prompt = (
            "Write exactly one short, motivational sentence for someone "
            "who is actively tracking their workouts."
        )

    ai_response    = model.generate_content(prompt)
    generated_text = ai_response.text.strip()

    # Include a motivational image roughly 30 % of the time
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

    # Escape single quotes in content to prevent SQL errors
    safe_content = content.replace("'", "\\'")

    query = f"""
        INSERT INTO {_table('Posts')} (PostId, AuthorId, Timestamp, ImageUrl, Content)
        VALUES ('{post_id}', '{user_id}', '{current_time}', NULL, '{safe_content}')
    """

    query_job = client.query(query)
    query_job.result()
=======


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

def get_all_calendar_events(user_id):
    """Fetches all workouts and formats them beautifully for the Streamlit Calendar."""
    from google.cloud import bigquery
    client = bigquery.Client()
    
    # Fetch everything for this user
    query = f"""
        SELECT WorkoutId, WorkoutType, StartTimestamp, TotalTimeMinutes, IsScheduled
        FROM {_table('Workouts')}
        WHERE UserId = '{user_id}'
    """
    results = client.query(query).result()
    
    events = []
    for row in results:
        # Check if it's a future scheduled workout
        is_scheduled = row.IsScheduled if hasattr(row, 'IsScheduled') else False
        
        # 1. Color Coding Logic
        if is_scheduled:
            # Planned AI Workouts: Soft Blue
            bg_color = "#E0E7FF" 
            border_color = "#6366F1" 
            text_color = "#3730A3"
            icon = "⏱️"
        else:
            # Completed Workouts: Solid Green
            bg_color = "#DCFCE7" 
            border_color = "#22C55E" 
            text_color = "#166534"
            icon = "✅"
            
        # 2. Build the Title
        time_mins = row.TotalTimeMinutes if hasattr(row, 'TotalTimeMinutes') and row.TotalTimeMinutes else 0
        
        # Safe extraction of WorkoutType
        raw_type = row.WorkoutType if hasattr(row, 'WorkoutType') and row.WorkoutType is not None else "Workout"
        workout_name = raw_type.replace(" (AI Suggestion)", "") 
        
        title = f"{icon} {workout_name} ({time_mins}m)"
        
        # 3. Format exactly as FullCalendar expects
        events.append({
            "title": title,
            "start": str(row.StartTimestamp), # ISO format works perfectly
            "backgroundColor": bg_color,
            "borderColor": border_color,
            "textColor": text_color,
            "display": "block" # Makes it look like a solid block
        })
        
    return events


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

    distance = 0.0
    avg_speed = 0.0
    elevation_gain = 0
    difficulty = "N/A"

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
    elif workout_type == "Cycling":
        distance = workout_data.get("miles", 0.0)
        avg_speed = workout_data.get("avg_speed", 0.0)
        
    elif workout_type == "Hiking":
       
        distance = workout_data.get("miles", 0.0)
        elevation_gain = workout_data.get("elevation_gain", 0)
        difficulty = workout_data.get("difficulty", "Moderate")
    else:
        distance = 0.0 # Gym doesn't track distance
    
    workout_query = f"""
        INSERT INTO {_table('Workouts')} 
        (WorkoutId, UserId, WorkoutType, StartTimestamp, EndTimestamp, TotalDistance, CaloriesBurned, 
         TotalTimeMinutes, HeartRateAvg, HeartRatePeak, TotalSteps, AvgSpeed, ElevationGain, Difficulty) 
        VALUES 
        ('{workout_id}', '{user_id}', '{workout_type}', '{start_ts}', '{end_ts}', {distance}, {calories}, 
         {total_time}, {hr_avg}, {hr_peak}, 0, {avg_speed}, {elevation_gain}, '{difficulty}')
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

# ===========================================================================
# AI functions
# ===========================================================================

def generate_ai_workout_plan(user_id):
    """Generates 5 workout suggestions from GenAI in JSON format."""

    
    vertexai.init(project=GCP_PROJECT_ID, location="us-central1")
    # Using JSON mode ensures Python can easily parse the 5 options
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
        # Convert the AI's string response into a Python list of dictionaries
        return json.loads(response.text)
    except Exception:
        return []

def schedule_ai_workout(user_id, workout_type, future_date, total_time):
    """Saves a future workout to the database as an AI Suggestion."""
    from google.cloud import bigquery
    import uuid
    client = bigquery.Client()
    
    workout_id = str(uuid.uuid4())
    # Save the future date at noon just as a placeholder time
    scheduled_ts = f"{future_date} 12:00:00"
    
    # We set IsScheduled to TRUE, and add '(AI Suggestion)' to the type
    query = f"""
        INSERT INTO {_table('Workouts')} 
        (WorkoutId, UserId, WorkoutType, StartTimestamp, EndTimestamp, TotalTimeMinutes, IsScheduled, TotalSteps) 
        VALUES 
        ('{workout_id}', '{user_id}', '{workout_type} (AI Suggestion)', '{scheduled_ts}', '{scheduled_ts}', {total_time}, TRUE, 0)
    """
    client.query(query).result()

def get_scheduled_workouts(user_id):
    """Fetches only future scheduled workouts."""
    from google.cloud import bigquery
    client = bigquery.Client()
    
    query = f"""
        SELECT WorkoutId, WorkoutType, StartTimestamp, TotalTimeMinutes
        FROM {_table('Workouts')}
        WHERE UserId = '{user_id}' AND IsScheduled = TRUE
        ORDER BY StartTimestamp ASC
    """
    return list(client.query(query).result())

def delete_workout(workout_id):
    """Deletes a specific workout by ID."""
    from google.cloud import bigquery
    client = bigquery.Client()
    query = f"DELETE FROM {_table('Workouts')} WHERE WorkoutId = '{workout_id}'"
    client.query(query).result()
>>>>>>> main
