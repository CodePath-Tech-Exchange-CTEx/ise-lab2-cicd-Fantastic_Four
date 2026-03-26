import streamlit as st
from data_fetcher import get_user_workouts, create_shared_post

def show_activity_page(user_id):

    # ── Premium CSS ──────────────────────────────────────────────────────────
    st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Syne:wght@400;600;700;800&family=DM+Sans:ital,wght@0,300;0,400;0,500;1,300&display=swap');

    /* Global */
    [data-testid="stAppViewContainer"] { background: #0a0a0f; }
    [data-testid="stHeader"] { background: transparent; }
    section[data-testid="stSidebar"] { background: #0f0f18; }

    /* Typography base */
    html, body, [class*="css"] {
        font-family: 'DM Sans', sans-serif;
        color: #e8e8f0;
    }

    /* Hero header */
    .hero-header {
        padding: 2.5rem 0 1.5rem 0;
        border-bottom: 1px solid rgba(255,255,255,0.06);
        margin-bottom: 2rem;
    }
    .hero-label {
        font-family: 'DM Sans', sans-serif;
        font-size: 0.7rem;
        font-weight: 500;
        letter-spacing: 0.18em;
        text-transform: uppercase;
        color: #6e6e9a;
        margin-bottom: 0.5rem;
    }
    .hero-title {
        font-family: 'Syne', sans-serif;
        font-size: 3.2rem;
        font-weight: 800;
        line-height: 1.05;
        background: linear-gradient(135deg, #ffffff 0%, #a78bfa 50%, #60a5fa 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        margin: 0;
    }

    /* Section headers */
    .section-label {
        font-family: 'DM Sans', sans-serif;
        font-size: 0.65rem;
        font-weight: 500;
        letter-spacing: 0.2em;
        text-transform: uppercase;
        color: #6e6e9a;
        margin-bottom: 1rem;
        margin-top: 2rem;
    }

    /* Stat cards */
    .stat-grid {
        display: grid;
        grid-template-columns: repeat(3, 1fr);
        gap: 1rem;
        margin-bottom: 2rem;
    }
    .stat-card {
        background: linear-gradient(145deg, #13131f, #1a1a2e);
        border: 1px solid rgba(167, 139, 250, 0.12);
        border-radius: 16px;
        padding: 1.5rem;
        position: relative;
        overflow: hidden;
        transition: border-color 0.3s ease;
    }
    .stat-card::before {
        content: '';
        position: absolute;
        top: 0; left: 0; right: 0;
        height: 2px;
        background: linear-gradient(90deg, #a78bfa, #60a5fa);
        opacity: 0.6;
    }
    .stat-card:hover { border-color: rgba(167, 139, 250, 0.3); }
    .stat-icon {
        font-size: 1.4rem;
        margin-bottom: 0.75rem;
        display: block;
    }
    .stat-value {
        font-family: 'Syne', sans-serif;
        font-size: 2rem;
        font-weight: 700;
        color: #ffffff;
        line-height: 1;
        margin-bottom: 0.3rem;
    }
    .stat-label {
        font-size: 0.75rem;
        color: #6e6e9a;
        font-weight: 400;
        letter-spacing: 0.05em;
    }

    /* Workout cards */
    .workout-card {
        background: #13131f;
        border: 1px solid rgba(255,255,255,0.06);
        border-radius: 16px;
        padding: 1.5rem;
        margin-bottom: 1rem;
        display: flex;
        align-items: center;
        gap: 1.5rem;
        transition: border-color 0.3s, transform 0.2s;
    }
    .workout-card:hover {
        border-color: rgba(167, 139, 250, 0.2);
        transform: translateX(4px);
    }
    .workout-index {
        font-family: 'Syne', sans-serif;
        font-size: 2.5rem;
        font-weight: 800;
        color: rgba(167, 139, 250, 0.15);
        min-width: 3rem;
        line-height: 1;
    }
    .workout-info { flex: 1; }
    .workout-date {
        font-size: 0.7rem;
        letter-spacing: 0.12em;
        text-transform: uppercase;
        color: #6e6e9a;
        margin-bottom: 0.4rem;
    }
    .workout-stats {
        display: flex;
        gap: 1.5rem;
        flex-wrap: wrap;
    }
    .workout-stat {
        display: flex;
        flex-direction: column;
    }
    .workout-stat-value {
        font-family: 'Syne', sans-serif;
        font-size: 1.1rem;
        font-weight: 600;
        color: #e8e8f0;
    }
    .workout-stat-label {
        font-size: 0.68rem;
        color: #6e6e9a;
        letter-spacing: 0.08em;
    }

    /* Share section */
    .share-section {
        background: linear-gradient(145deg, #13131f, #1a1428);
        border: 1px solid rgba(167, 139, 250, 0.15);
        border-radius: 20px;
        padding: 2rem;
        margin-top: 2rem;
    }
    .share-title {
        font-family: 'Syne', sans-serif;
        font-size: 1.4rem;
        font-weight: 700;
        color: #ffffff;
        margin-bottom: 0.3rem;
    }
    .share-subtitle {
        font-size: 0.85rem;
        color: #6e6e9a;
        margin-bottom: 1.5rem;
    }
    .preview-box {
        background: rgba(255,255,255,0.03);
        border: 1px solid rgba(255,255,255,0.08);
        border-radius: 12px;
        padding: 1rem 1.25rem;
        font-size: 0.9rem;
        color: #b0b0c8;
        margin-bottom: 1.5rem;
        font-style: italic;
        line-height: 1.5;
    }

    /* Streamlit overrides */
    div[data-testid="stSelectbox"] label { color: #6e6e9a !important; font-size: 0.75rem !important; letter-spacing: 0.1em; }
    div[data-testid="stTextArea"] label { color: #6e6e9a !important; font-size: 0.75rem !important; letter-spacing: 0.1em; }
    .stButton > button {
        background: linear-gradient(135deg, #a78bfa, #60a5fa) !important;
        color: #000 !important;
        font-family: 'Syne', sans-serif !important;
        font-weight: 700 !important;
        font-size: 0.85rem !important;
        letter-spacing: 0.08em !important;
        border: none !important;
        border-radius: 10px !important;
        padding: 0.65rem 2rem !important;
        transition: opacity 0.2s !important;
    }
    .stButton > button:hover { opacity: 0.85 !important; }
    .stAlert { border-radius: 10px !important; }

    /* Hide streamlit branding */
    #MainMenu, footer { visibility: hidden; }
    </style>
    """, unsafe_allow_html=True)

    # ── Hero Header ──────────────────────────────────────────────────────────
    st.markdown("""
    <div class="hero-header">
        <div class="hero-label">Your Performance</div>
        <div class="hero-title">Activity<br>Dashboard</div>
    </div>
    """, unsafe_allow_html=True)

    # ── Fetch Data ───────────────────────────────────────────────────────────
    user_workouts = get_user_workouts(user_id)
    recent = user_workouts[:3]

    # ── Summary Stats ────────────────────────────────────────────────────────
    total_steps    = sum(w.get('steps', 0) or 0 for w in user_workouts)
    total_calories = sum(w.get('calories_burned', 0) or 0 for w in user_workouts)
    total_distance = sum(w.get('distance', 0) or 0 for w in user_workouts)

    st.markdown('<div class="section-label">Overall Summary</div>', unsafe_allow_html=True)
    st.markdown(f"""
    <div class="stat-grid">
        <div class="stat-card">
            <span class="stat-icon">👟</span>
            <div class="stat-value">{total_steps:,}</div>
            <div class="stat-label">Total Steps</div>
        </div>
        <div class="stat-card">
            <span class="stat-icon">🔥</span>
            <div class="stat-value">{total_calories:,.0f}</div>
            <div class="stat-label">Calories Burned</div>
        </div>
        <div class="stat-card">
            <span class="stat-icon">📍</span>
            <div class="stat-value">{total_distance:.1f}</div>
            <div class="stat-label">km Covered</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # ── Recent Workouts ──────────────────────────────────────────────────────
    st.markdown('<div class="section-label">Recent Workouts</div>', unsafe_allow_html=True)

    if not recent:
        st.markdown('<p style="color:#6e6e9a; font-size:0.9rem;">No workouts logged yet.</p>', unsafe_allow_html=True)
    else:
        for i, w in enumerate(recent):
            date_str = str(w.get('start_timestamp', ''))[:16].replace('T', ' ') if w.get('start_timestamp') else 'Unknown date'
            steps    = f"{w.get('steps', 0):,}" if w.get('steps') else '—'
            cals     = f"{w.get('calories_burned', 0):.0f} kcal" if w.get('calories_burned') else '—'
            dist     = f"{w.get('distance', 0):.1f} km" if w.get('distance') else '—'

            st.markdown(f"""
            <div class="workout-card">
                <div class="workout-index">0{i+1}</div>
                <div class="workout-info">
                    <div class="workout-date">{date_str}</div>
                    <div class="workout-stats">
                        <div class="workout-stat">
                            <span class="workout-stat-value">{steps}</span>
                            <span class="workout-stat-label">Steps</span>
                        </div>
                        <div class="workout-stat">
                            <span class="workout-stat-value">{cals}</span>
                            <span class="workout-stat-label">Calories</span>
                        </div>
                        <div class="workout-stat">
                            <span class="workout-stat-value">{dist}</span>
                            <span class="workout-stat-label">Distance</span>
                        </div>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)

    # ── Share Section ────────────────────────────────────────────────────────
    st.markdown('<div class="share-section">', unsafe_allow_html=True)
    st.markdown("""
    <div class="share-title">Share Your Progress</div>
    <div class="share-subtitle">Post a stat to your community feed</div>
    """, unsafe_allow_html=True)

    stat_choice = st.selectbox(
        "CHOOSE A STAT TO SHARE",
        ["Steps", "Calories Burned", "Distance"],
        key="stat_choice"
    )

    if stat_choice == "Steps":
        default_msg = f"Just hit {total_steps:,} steps — who's keeping up? 👟"
    elif stat_choice == "Calories Burned":
        default_msg = f"Burned {total_calories:.0f} calories and not stopping. 🔥"
    else:
        default_msg = f"Covered {total_distance:.1f} km — every meter counts. 📍"

    custom_msg = st.text_area(
        "CUSTOMIZE YOUR MESSAGE",
        value=default_msg,
        height=80,
        key="custom_msg"
    )

    st.markdown(f'<div class="preview-box">"{custom_msg}"</div>', unsafe_allow_html=True)

    if st.button("🚀 Post to Community"):
        try:
            create_shared_post(user_id, custom_msg)
            st.success("Posted to your community feed!")
            st.balloons()
        except Exception as e:
            st.error(f"Something went wrong: {e}")

    st.markdown('</div>', unsafe_allow_html=True)
