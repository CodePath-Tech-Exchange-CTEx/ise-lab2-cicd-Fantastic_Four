#############################################################################
# data_fetcher.py
#
# This file contains functions to fetch data needed for the app.
#############################################################################

import datetime
import random
import uuid

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

    # Collect friends first (single pass — avoids re-iteration issues)
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

    # Grab profile once so we have username / avatar for every post
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

def verify_login(Username, passowrd):
    """
    creadentials check
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
