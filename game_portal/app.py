
import streamlit as st
import sqlite3
import hashlib
from pathlib import Path
from datetime import datetime

st.set_page_config(
    page_title="RetroArc",
    page_icon="🎮",
    layout="wide"
)

DB_PATH = Path(__file__).parent / "retroarc.db"

def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    with get_db() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                email TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL
            )
        """)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS progress (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                game_name TEXT NOT NULL,
                high_score INTEGER DEFAULT 0,
                games_played INTEGER DEFAULT 0,
                total_wins INTEGER DEFAULT 0,
                last_played TEXT,
                UNIQUE(user_id, game_name),
                FOREIGN KEY(user_id) REFERENCES users(id)
            )
        """)

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def create_user(username, email, password):
    try:
        with get_db() as conn:
            cursor = conn.execute(
                "INSERT INTO users(username,email,password_hash) "
                "VALUES(?,?,?)",
                (username, email, hash_password(password))
            )
            user_id = cursor.lastrowid

            for game in ["pong", "snake", "states"]:
                conn.execute(
                    "INSERT INTO progress(user_id,game_name) VALUES(?,?)",
                    (user_id, game)
                )
        return True, "Account created successfully!"
    except sqlite3.IntegrityError:
        return False, "Username or email already exists."

def login_user(username, password):
    with get_db() as conn:
        user = conn.execute(
            "SELECT * FROM users WHERE username=?",
            (username,)
        ).fetchone()

    if user and user["password_hash"] == hash_password(password):
        return user["id"], user["username"]
    return None, None

init_db()

if "user_id" not in st.session_state:
    st.session_state.user_id = None
    st.session_state.username = None

st.markdown("""
<style>
.stApp {
    background: #101014;
    color: #F5F5F5;
}
h1, h2, h3 {
    color: #FFB347;
}
div.stButton > button {
    background: #FF8C42;
    color: #101014;
    border-radius: 10px;
    border: none;
    font-weight: bold;
}
</style>
""", unsafe_allow_html=True)

def logout():
    st.session_state.user_id = None
    st.session_state.username = None
    st.rerun()

def show_login():
    st.title("🎮 RetroArc")
    st.subheader("Your arcade. Your adventure.")
    tab1, tab2 = st.tabs(["Login", "Create Account"])

    with tab1:
        with st.form("login_form"):
            username = st.text_input("Username")
            password = st.text_input("Password", type="password")
            submitted = st.form_submit_button("Login", use_container_width=True)

        if submitted:
            uid, name = login_user(username, password)
            if uid:
                st.session_state.user_id = uid
                st.session_state.username = name
                st.rerun()
            else:
                st.error("Invalid username or password.")

    with tab2:
        with st.form("register_form"):
            username = st.text_input("Choose a username")
            email = st.text_input("Email address")
            password = st.text_input("Create password", type="password")
            confirm = st.text_input("Confirm password", type="password")
            submitted = st.form_submit_button(
                "Create Account", use_container_width=True
            )

        if submitted:
            if not username.strip() or not email.strip() or not password:
                st.warning("Please complete every field.")
            elif password != confirm:
                st.error("Passwords do not match.")
            elif len(password) < 8:
                st.error("Use a password of at least 8 characters.")
            else:
                ok, message = create_user(
                    username.strip(), email.strip(), password
                )
                if ok:
                    st.success(message)
                else:
                    st.error(message)

def show_dashboard():
    uid = st.session_state.user_id

    with st.sidebar:
        st.title("🕹️ RetroArc")
        st.write(f"Player: **{st.session_state.username}**")
        if st.button("Logout", use_container_width=True):
            logout()

    st.title(f"Welcome back, {st.session_state.username}! 👾")
    st.write("Choose a game and beat your high score.")

    with get_db() as conn:
        stats = conn.execute(
            "SELECT * FROM progress WHERE user_id=?",
            (uid,)
        ).fetchall()

    total_played = sum(row["games_played"] for row in stats)
    total_wins = sum(row["total_wins"] for row in stats)
    best_score = max((row["high_score"] for row in stats), default=0)

    a, b, c = st.columns(3)
    a.metric("Games Played", total_played)
    b.metric("Total Wins", total_wins)
    c.metric("Best Score", best_score)

    st.divider()
    st.subheader("🕹️ Arcade")

    games = [
        ("🐍 Snake", "snake", "Eat, grow, and beat your record."),
        ("🏓 Pong", "pong", "Test your reflexes."),
        ("🌎 States Challenge", "states", "Challenge your geography knowledge.")
    ]

    columns = st.columns(3)

    for column, (title, game, description) in zip(columns, games):
        row = next((r for r in stats if r["game_name"] == game), None)

        with column:
            st.markdown(f"### {title}")
            st.write(description)
            st.metric("High Score", row["high_score"] if row else 0)
            st.caption(
                f"Played {row['games_played'] if row else 0} times"
            )

            if st.button("Open Game", key=f"open_{game}",
                         use_container_width=True):
                st.session_state.selected_game = game
                st.rerun()

    selected = st.session_state.get("selected_game")

    if selected:
        st.divider()
        st.subheader(f"🎮 {selected.title()}")

        st.info(
            "This is the Streamlit game area. Your original HTML gameplay "
            "must be integrated here to make the game playable."
        )

        with st.form(f"score_{selected}"):
            score = st.number_input(
                "Record a score", min_value=0, step=1
            )
            won = st.checkbox("I won this round")
            submitted = st.form_submit_button("Save Result")

        if submitted:
            with get_db() as conn:
                conn.execute("""
                    INSERT OR IGNORE INTO progress(user_id,game_name)
                    VALUES(?,?)
                """, (uid, selected))

                conn.execute("""
                    UPDATE progress
                    SET high_score=MAX(high_score, ?),
                        games_played=games_played+1,
                        total_wins=total_wins+?,
                        last_played=?
                    WHERE user_id=? AND game_name=?
                """, (
                    score, int(won), datetime.utcnow().isoformat(),
                    uid, selected
                ))

            st.success("Result saved!")
            st.rerun()

        if st.button("Back to Dashboard"):
            del st.session_state.selected_game
            st.rerun()

if st.session_state.user_id is None:
    show_login()
else:
    show_dashboard()
