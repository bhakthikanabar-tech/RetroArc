import os
import hmac
import hashlib
import random
import sqlite3
import streamlit as st
from pathlib import Path
from datetime import datetime

# ==================================================
# CONFIGURATION
# ==================================================

st.set_page_config(
    page_title="RetroArc | Arcade",
    page_icon="🎮",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Use a writable location on Streamlit Cloud.
# Note: /tmp data can disappear after a restart.
DB_PATH = Path(os.getenv("RETROARC_DB_PATH", "/tmp/retroarc.db"))

GAMES = {
    "snake": {
        "name": "Snake",
        "emoji": "🐍",
        "description": "Eat, grow, and beat your best score.",
    },
    "pong": {
        "name": "Pong",
        "emoji": "🏓",
        "description": "A quick reflex challenge.",
    },
    "states": {
        "name": "States Challenge",
        "emoji": "🌎",
        "description": "Test your knowledge of Indian states and capitals.",
    },
}

# ==================================================
# PREMIUM RETRO-NEON DESIGN
# ==================================================

st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;500;600;700;800&family=Inter:wght@400;500;600;700&display=swap');

    :root {
        --bg: #0B0B14;
        --panel: #141421;
        --purple: #A855F7;
        --cyan: #22D3EE;
        --pink: #F472B6;
        --white: #F5F3FF;
        --muted: #A1A1B8;
    }

    .stApp {
        background:
            radial-gradient(ellipse at 8% 0%, #24133F 0%, transparent 36%),
            radial-gradient(ellipse at 100% 20%, #102238 0%, transparent 32%),
            var(--bg);
        color: var(--white);
        font-family: 'Inter', sans-serif;
    }

    [data-testid="stHeader"] {
        background: transparent;
    }

    .block-container {
        max-width: 1200px;
        padding-top: 2rem;
        padding-bottom: 3rem;
    }

    h1, h2, h3 {
        font-family: 'Orbitron', sans-serif !important;
        letter-spacing: -0.4px;
        color: var(--white) !important;
    }

    h3 {
        color: #D8B4FE !important;
    }

    p, label, .stMarkdown {
        color: var(--white);
    }

    [data-testid="stSidebar"] {
        background: #10101C;
        border-right: 1px solid #29243D;
    }

    [data-testid="stSidebar"] h1 {
        color: var(--purple) !important;
    }

    [data-testid="stMetric"] {
        background: linear-gradient(145deg, #19192A, #11111D);
        border: 1px solid #302747;
        border-radius: 16px;
        padding: 18px;
    }

    [data-testid="stMetricLabel"] {
        color: var(--muted) !important;
    }

    [data-testid="stMetricValue"] {
        color: var(--cyan) !important;
        font-family: 'Orbitron', sans-serif;
    }

    div.stButton > button,
    div.stFormSubmitButton > button {
        background: linear-gradient(100deg, #9333EA, #7C3AED);
        color: white;
        border: 1px solid #C084FC;
        border-radius: 10px;
        min-height: 43px;
        font-weight: 700;
        transition: all 0.2s ease;
    }

    div.stButton > button:hover,
    div.stFormSubmitButton > button:hover {
        background: linear-gradient(100deg, #A855F7, #9333EA);
        border-color: var(--cyan);
        box-shadow: 0 0 18px #A855F733;
        color: white;
        transform: translateY(-1px);
    }

    [data-testid="stForm"] {
        background: #141421;
        border: 1px solid #302747;
        padding: 22px;
        border-radius: 16px;
    }

    input, textarea {
        background: #10101C !important;
        color: white !important;
        border-color: #39334E !important;
    }

    [data-baseweb="tab-list"] {
        gap: 10px;
        border-bottom: 1px solid #302747;
    }

    button[data-baseweb="tab"][aria-selected="true"] {
        color: var(--cyan) !important;
        border-bottom: 2px solid var(--cyan);
    }

    hr {
        border-color: #302747 !important;
    }

    .arcade-hero {
        padding: 30px;
        border-radius: 20px;
        background: linear-gradient(120deg, #211238, #111827 75%);
        border: 1px solid #59358A;
        margin-bottom: 20px;
    }

    .eyebrow {
        color: var(--cyan);
        letter-spacing: 4px;
        font-size: 11px;
        font-weight: 800;
    }

    .game-card {
        min-height: 190px;
        padding: 20px;
        border-radius: 16px;
        border: 1px solid #302747;
        background: linear-gradient(145deg, #19192A, #11111D);
    }

    .game-icon {
        font-size: 38px;
    }

    .game-kicker {
        color: var(--cyan);
        letter-spacing: 2px;
        font-size: 10px;
        font-weight: 800;
    }

    .muted {
        color: var(--muted);
    }

    #MainMenu, footer {
        visibility: hidden;
    }

    @media (max-width: 768px) {
        .block-container {
            padding: 1rem 0.8rem 2rem;
        }

        .arcade-hero {
            padding: 20px;
        }
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# ==================================================
# DATABASE
# ==================================================

def db_connect():
    connection = sqlite3.connect(
        str(DB_PATH),
        timeout=30,
        check_same_thread=False,
    )
    connection.row_factory = sqlite3.Row
    connection.execute("PRAGMA foreign_keys=ON")
    return connection


def init_db():
    with db_connect() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT NOT NULL COLLATE NOCASE UNIQUE,
                email TEXT NOT NULL COLLATE NOCASE UNIQUE,
                password_hash TEXT NOT NULL,
                created_at TEXT NOT NULL
            )
        """)

        conn.execute("""
            CREATE TABLE IF NOT EXISTS progress (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                game_name TEXT NOT NULL,
                high_score INTEGER NOT NULL DEFAULT 0,
                games_played INTEGER NOT NULL DEFAULT 0,
                total_wins INTEGER NOT NULL DEFAULT 0,
                last_played TEXT,
                UNIQUE(user_id, game_name),
                FOREIGN KEY(user_id)
                    REFERENCES users(id) ON DELETE CASCADE
            )
        """)


def password_hash(password, salt=None):
    salt = salt or os.urandom(16)
    digest = hashlib.pbkdf2_hmac(
        "sha256",
        password.encode("utf-8"),
        salt,
        310_000,
    )
    return salt.hex() + ":" + digest.hex()


def verify_password(password, stored):
    try:
        salt_hex, digest_hex = stored.split(":", 1)
        salt = bytes.fromhex(salt_hex)
        check = password_hash(password, salt).split(":", 1)[1]
        return hmac.compare_digest(check, digest_hex)
    except (ValueError, TypeError):
        return False


def register_user(username, email, password):
    username = username.strip()
    email = email.strip().lower()

    if not username or not email or not password:
        return False, "Please complete all fields."

    if len(username) < 3:
        return False, "Username must contain at least 3 characters."

    if len(password) < 8:
        return False, "Password must be at least 8 characters."

    if "@" not in email or "." not in email.rsplit("@", 1)[-1]:
        return False, "Enter a valid email address."

    try:
        with db_connect() as conn:
            cursor = conn.execute(
                """
                INSERT INTO users
                (username, email, password_hash, created_at)
                VALUES (?, ?, ?, ?)
                """,
                (
                    username,
                    email,
                    password_hash(password),
                    datetime.utcnow().isoformat(),
                ),
            )

            user_id = cursor.lastrowid

            conn.executemany(
                "INSERT INTO progress(user_id, game_name) VALUES (?, ?)",
                [(user_id, game) for game in GAMES],
            )

        return True, "Account created! You can now log in."

    except sqlite3.IntegrityError:
        return False, "That username or email is already registered."


def authenticate(username, password):
    with db_connect() as conn:
        user = conn.execute(
            "SELECT * FROM users WHERE username=? COLLATE NOCASE",
            (username.strip(),),
        ).fetchone()

    if user and verify_password(password, user["password_hash"]):
        return {
            "id": user["id"],
            "username": user["username"],
        }

    return None


def get_progress(user_id):
    with db_connect() as conn:
        conn.executemany(
            "INSERT OR IGNORE INTO progress(user_id, game_name) VALUES (?, ?)",
            [(user_id, game) for game in GAMES],
        )

        rows = conn.execute(
            "SELECT * FROM progress WHERE user_id=?",
            (user_id,),
        ).fetchall()

    return {row["game_name"]: dict(row) for row in rows}


def save_result(user_id, game, score, won=False):
    with db_connect() as conn:
        conn.execute(
            "INSERT OR IGNORE INTO progress(user_id, game_name) VALUES (?, ?)",
            (user_id, game),
        )

        conn.execute(
            """
            UPDATE progress
            SET high_score = MAX(high_score, ?),
                games_played = games_played + 1,
                total_wins = total_wins + ?,
                last_played = ?
            WHERE user_id = ? AND game_name = ?
            """,
            (
                int(score),
                int(won),
                datetime.utcnow().isoformat(),
                user_id,
                game,
            ),
        )


init_db()

# ==================================================
# SESSION STATE
# ==================================================

defaults = {
    "user_id": None,
    "username": None,
    "page": "home",
    "selected_game": None,
    "snake_score": 0,
    "snake_over": False,
    "states_q": None,
    "states_correct": 0,
    "states_answered": 0,
    "states_options": [],
    "pong_score": 0,
}

for key, value in defaults.items():
    if key not in st.session_state:
        st.session_state[key] = value


def logout():
    for key in defaults:
        if key != "page":
            st.session_state[key] = defaults[key]

    st.session_state.page = "home"
    st.rerun()


# ==================================================
# SHARED UI
# ==================================================

def hero(kicker, title, subtitle):
    st.markdown(
        f"""
        <div class="arcade-hero">
            <div class="eyebrow">{kicker}</div>
            <h1 style="margin:12px 0 8px;">{title}</h1>
            <p style="color:#B9B6D0;margin-bottom:0;">{subtitle}</p>
        </div>
        """,
        unsafe_allow_html=True,
    )


def sidebar():
    with st.sidebar:
        st.markdown("# 🕹️ RETROARC")
        st.caption("THE PIXEL PLAYGROUND")
        st.divider()

        if st.session_state.user_id:
            st.markdown(f"**PLAYER**  \n{st.session_state.username}")
            st.divider()

            if st.button("🏠 Dashboard", use_container_width=True):
                st.session_state.page = "dashboard"
                st.session_state.selected_game = None
                st.rerun()

            if st.button("🎮 Arcade", use_container_width=True):
                st.session_state.page = "arcade"
                st.session_state.selected_game = None
                st.rerun()

            st.divider()

            if st.button("↪ Log out", use_container_width=True):
                logout()
        else:
            st.caption("LOG IN TO SAVE YOUR SCORES")

        st.markdown("---")
        st.caption("RETROARC • PLAY YOUR WAY")


def render_game_cards(progress):
    columns = st.columns(3, gap="medium")

    for column, (key, info) in zip(columns, GAMES.items()):
        stats = progress.get(key, {})

        with column:
            st.markdown(
                f"""
                <div class="game-card">
                    <div class="game-icon">{info['emoji']}</div>
                    <div class="game-kicker">ARCADE GAME</div>
                    <h3 style="margin:10px 0;">{info['name']}</h3>
                    <p class="muted" style="font-size:13px;min-height:40px;">
                        {info['description']}
                    </p>
                </div>
                """,
                unsafe_allow_html=True,
            )

            first, second = st.columns(2)
            first.metric("BEST SCORE", stats.get("high_score", 0))
            second.metric("PLAYED", stats.get("games_played", 0))

            if st.button(
                "▶ PLAY NOW",
                key=f"play_{key}",
                use_container_width=True,
            ):
                st.session_state.selected_game = key
                st.session_state.page = "game"
                st.rerun()


# ==================================================
# LOGIN AND REGISTRATION
# ==================================================

def show_auth():
    left, right = st.columns([1.1, 1], gap="large")

    with left:
        st.markdown(
            """
            <div style="padding:36px 8px 20px 0;">
                <div class="eyebrow">INSERT COIN • PRESS START</div>
                <h1 style="font-size:clamp(34px,5vw,58px);line-height:1.12;margin:20px 0 12px;">
                    WELCOME TO<br>
                    <span style="color:#A855F7;">RETRO</span><span style="color:#22D3EE;">ARC</span>
                </h1>
                <p style="font-size:17px;color:#B9B6D0;line-height:1.8;">
                    Your arcade. Your adventure.<br>
                    Play classic-inspired games, beat your personal best,
                    and build your legacy.
                </p>
                <div style="display:flex;gap:12px;flex-wrap:wrap;margin-top:26px;">
                    <span style="padding:9px 13px;border:1px solid #493268;border-radius:30px;color:#D8B4FE;">🐍 SNAKE</span>
                    <span style="padding:9px 13px;border:1px solid #24505C;border-radius:30px;color:#67E8F9;">🏓 PONG</span>
                    <span style="padding:9px 13px;border:1px solid #5B294B;border-radius:30px;color:#F9A8D4;">🌎 STATES</span>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with right:
        st.markdown(
            """
            <div class="arcade-hero">
                <div class="eyebrow">PLAYER ACCESS / 01</div>
                <h2 style="margin-top:12px;">ENTER THE ARCADE</h2>
                <p style="color:#B9B6D0;">Sign in to continue your journey.</p>
            </div>
            """,
            unsafe_allow_html=True,
        )

        login_tab, register_tab = st.tabs(["LOGIN", "CREATE ACCOUNT"])

        with login_tab:
            with st.form("login_form"):
                username = st.text_input(
                    "Username",
                    placeholder="Your player name",
                )
                password = st.text_input(
                    "Password",
                    type="password",
                    placeholder="Your password",
                )
                submitted = st.form_submit_button(
                    "▶ PRESS START",
                    use_container_width=True,
                )

            if submitted:
                user = authenticate(username, password)

                if user:
                    st.session_state.user_id = user["id"]
                    st.session_state.username = user["username"]
                    st.session_state.page = "dashboard"
                    st.rerun()
                else:
                    st.error("Username or password is incorrect.")

        with register_tab:
            with st.form("register_form"):
                new_username = st.text_input(
                    "Player name",
                    placeholder="At least 3 characters",
                )
                email = st.text_input(
                    "Email",
                    placeholder="you@example.com",
                )
                new_password = st.text_input(
                    "Password",
                    type="password",
                    placeholder="At least 8 characters",
                )
                confirm = st.text_input(
                    "Confirm password",
                    type="password",
                )
                submitted = st.form_submit_button(
                    "＋ CREATE PLAYER",
                    use_container_width=True,
                )

            if submitted:
                if new_password != confirm:
                    st.error("Passwords do not match.")
                else:
                    ok, message = register_user(
                        new_username,
                        email,
                        new_password,
                    )

                    if ok:
                        st.success(message)
                    else:
                        st.error(message)

        st.caption(
            "Create an account to track your scores. "
            "Cloud database persistence depends on your hosting setup."
        )


# ==================================================
# DASHBOARD
# ==================================================

def show_dashboard():
    progress = get_progress(st.session_state.user_id)

    total_played = sum(
        item["games_played"] for item in progress.values()
    )
    total_wins = sum(
        item["total_wins"] for item in progress.values()
    )
    best = max(
        [item["high_score"] for item in progress.values()] or [0]
    )

    hero(
        "PLAYER ZONE / ARCADE 01",
        f"WELCOME BACK, {st.session_state.username.upper()}!",
        "Your next high score is waiting. Choose a game and make it count.",
    )

    first, second, third = st.columns(3)
    first.metric("TOTAL GAMES PLAYED", total_played)
    second.metric("TOTAL WINS", total_wins)
    third.metric("PERSONAL BEST", best)

    st.markdown("## 🎮 YOUR ARCADE")
    st.caption("Pick your next challenge.")
    render_game_cards(progress)


def record_game(game, score, won=False):
    save_result(
        st.session_state.user_id,
        game,
        score,
        won,
    )
    st.toast("Score saved to your profile!", icon="✅")


# ==================================================
# SNAKE CHALLENGE
# ==================================================

def show_snake():
    st.subheader("🐍 Snake")
    st.write(
        "A turn-based Snake challenge. Use the direction buttons "
        "to advance and build your score."
    )

    if st.session_state.snake_over:
        st.warning(
            f"Round ended. Score: {st.session_state.snake_score}"
        )

        if st.button("Start a new round"):
            st.session_state.snake_score = 0
            st.session_state.snake_over = False
            st.rerun()

        return

    st.metric("ROUND SCORE", st.session_state.snake_score)
    st.info(
        "Each move advances one turn. This is a simplified "
        "Streamlit version, not a continuously animated Snake game."
    )

    top, middle, bottom = st.columns(3)

    with middle:
        up = st.button("⬆️", use_container_width=True)

    left, _, right = st.columns(3)

    with left:
        move_left = st.button("⬅️", use_container_width=True)

    with right:
        move_right = st.button("➡️", use_container_width=True)

    _, down_col, _ = st.columns(3)

    with down_col:
        move_down = st.button("⬇️", use_container_width=True)

    if up or move_left or move_right or move_down:
        if random.random() < 0.7:
            st.session_state.snake_score += 1
        else:
            st.session_state.snake_over = True
            record_game(
                "snake",
                st.session_state.snake_score,
                False,
            )

        st.rerun()

    if st.button("Finish and save score"):
        score = st.session_state.snake_score
        record_game("snake", score, score >= 10)
        st.session_state.snake_score = 0
        st.session_state.snake_over = False
        st.rerun()


# ==================================================
# INDIAN STATES AND CAPITALS QUIZ
# ==================================================

STATES = {
    "Andhra Pradesh": "Amaravati",
    "Arunachal Pradesh": "Itanagar",
    "Assam": "Dispur",
    "Bihar": "Patna",
    "Chhattisgarh": "Raipur",
    "Goa": "Panaji",
    "Gujarat": "Gandhinagar",
    "Haryana": "Chandigarh",
    "Himachal Pradesh": "Shimla",
    "Jharkhand": "Ranchi",
    "Karnataka": "Bengaluru",
    "Kerala": "Thiruvananthapuram",
    "Madhya Pradesh": "Bhopal",
    "Maharashtra": "Mumbai",
    "Manipur": "Imphal",
    "Meghalaya": "Shillong",
    "Mizoram": "Aizawl",
    "Nagaland": "Kohima",
    "Odisha": "Bhubaneswar",
    "Punjab": "Chandigarh",
    "Rajasthan": "Jaipur",
    "Sikkim": "Gangtok",
    "Tamil Nadu": "Chennai",
    "Telangana": "Hyderabad",
    "Tripura": "Agartala",
    "Uttar Pradesh": "Lucknow",
    "Uttarakhand": "Dehradun",
    "West Bengal": "Kolkata",
}


def new_states_question():
    state = random.choice(list(STATES.keys()))
    correct_capital = STATES[state]

    wrong_options = list(
        set(STATES.values()) - {correct_capital}
    )
    options = random.sample(wrong_options, 3)
    options.append(correct_capital)
    random.shuffle(options)

    st.session_state.states_q = state
    st.session_state.states_options = options


def show_states():
    st.subheader("🌎 States Challenge")
    st.write("Choose the correct capital for each Indian state.")

    if st.session_state.states_q is None:
        new_states_question()

    state = st.session_state.states_q

    st.markdown(f"### What is the capital of {state}?")

    answer = st.radio(
        "Choose one answer",
        st.session_state.states_options,
        key=f"state_answer_{st.session_state.states_answered}",
    )

    if st.button("Submit answer"):
        if answer == STATES[state]:
            st.session_state.states_correct += 1
            st.success("Correct! +1 point")
        else:
            st.error(
                f"Not quite. The capital of {state} is {STATES[state]}."
            )

        st.session_state.states_answered += 1
        st.session_state.states_q = None
        st.rerun()

    st.caption(
        f"Correct answers: {st.session_state.states_correct} • "
        f"Questions answered: {st.session_state.states_answered}"
    )

    if st.button("Finish quiz and save score"):
        score = st.session_state.states_correct
        record_game("states", score, score >= 5)

        st.session_state.states_q = None
        st.session_state.states_correct = 0
        st.session_state.states_answered = 0
        st.rerun()


# ==================================================
# PONG CHALLENGE
# ==================================================

def show_pong():
    st.subheader("🏓 Pong Challenge")
    st.write(
        "Build your rally score and try to reach 10 points. "
        "This is a simplified score challenge, not a real-time "
        "animated paddle-and-ball game."
    )

    st.markdown("### Challenge controls")
    st.metric("ROUND SCORE", st.session_state.pong_score)

    first, second, third = st.columns(3)

    with first:
        if st.button("🏓 Rally +1", use_container_width=True):
            st.session_state.pong_score += 1
            st.rerun()

    with second:
        if st.button("⚡ Rally +3", use_container_width=True):
            st.session_state.pong_score += 3
            st.rerun()

    with third:
        if st.button("🏁 End round", use_container_width=True):
            score = st.session_state.pong_score
            record_game("pong", score, score >= 10)
            st.session_state.pong_score = 0
            st.rerun()


# ==================================================
# GAME PAGE
# ==================================================

def show_game():
    game = st.session_state.selected_game

    if game not in GAMES:
        st.session_state.page = "dashboard"
        st.rerun()

    info = GAMES[game]

    hero(
        "NOW PLAYING / PLAYER 01",
        f"{info['emoji']} {info['name'].upper()}",
        info["description"],
    )

    if st.button("← BACK TO ARCADE"):
        st.session_state.page = "dashboard"
        st.session_state.selected_game = None
        st.rerun()

    st.divider()

    if game == "snake":
        show_snake()
    elif game == "pong":
        show_pong()
    elif game == "states":
        show_states()


# ==================================================
# MAIN APP ROUTER
# ==================================================

if st.session_state.user_id is None:
    show_auth()
else:
    sidebar()

    if st.session_state.page == "game":
        show_game()

    elif st.session_state.page == "arcade":
        hero(
            "SELECT YOUR CHALLENGE",
            "THE ARCADE",
            "Three challenges. One player. How high can you score?",
        )
        render_game_cards(
            get_progress(st.session_state.user_id)
        )

    else:
        show_dashboard()
