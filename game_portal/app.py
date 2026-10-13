import os, textwrap, zipfile

base = "/mnt/data/retroarc_streamlit"
os.makedirs(base, exist_ok=True)
os.makedirs(os.path.join(base, ".streamlit"), exist_ok=True)

app_code = r'''import os
import hmac
import hashlib
import sqlite3
import random
import streamlit as st
from pathlib import Path
from datetime import datetime

# -------------------- CONFIG --------------------
st.set_page_config(
    page_title="RetroArc | Arcade",
    page_icon="🎮",
    layout="wide",
    initial_sidebar_state="expanded",
)

APP_DIR = Path(__file__).parent
DB_PATH = Path(os.getenv("RETROARC_DB_PATH", str(APP_DIR / "retroarc.db")))
GAMES = {
    "snake": {"name": "Snake", "emoji": "🐍", "description": "Eat, grow, and beat your best score.", "color": "#A855F7"},
    "pong": {"name": "Pong", "emoji": "🏓", "description": "A quick reflex challenge.", "color": "#22D3EE"},
    "states": {"name": "States Challenge", "emoji": "🌎", "description": "Test your Indian states and capitals knowledge.", "color": "#F472B6"},
}

# -------------------- STYLE --------------------
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;500;600;700;800&family=Inter:wght@400;500;600;700&display=swap');
:root { --bg:#0B0B14; --panel:#141421; --purple:#A855F7; --cyan:#22D3EE; --pink:#F472B6; --white:#F5F3FF; --muted:#A1A1B8; }
.stApp { background: radial-gradient(ellipse at 8% 0%, #24133F 0%, transparent 36%), radial-gradient(ellipse at 100% 20%, #102238 0%, transparent 32%), var(--bg); color:var(--white); font-family:'Inter',sans-serif; }
[data-testid="stHeader"] { background:transparent; }
.block-container { max-width:1200px; padding-top:2rem; padding-bottom:3rem; }
h1,h2,h3 { font-family:'Orbitron',sans-serif !important; letter-spacing:-.4px; }
h1 { color:var(--white) !important; font-weight:800 !important; }
h2 { color:var(--white) !important; }
h3 { color:#D8B4FE !important; }
p,label,.stMarkdown { color:var(--white); }
[data-testid="stSidebar"] { background:#10101C; border-right:1px solid #29243D; }
[data-testid="stSidebar"] h1 { color:var(--purple) !important; font-size:1.45rem !important; }
[data-testid="stMetric"] { background:linear-gradient(145deg,#19192A,#11111D); border:1px solid #302747; border-radius:16px; padding:18px; }
[data-testid="stMetricLabel"] { color:var(--muted) !important; }
[data-testid="stMetricValue"] { color:var(--cyan) !important; font-family:'Orbitron',sans-serif; }
div.stButton > button, div.stFormSubmitButton > button { background:linear-gradient(100deg,#9333EA,#7C3AED); color:white; border:1px solid #C084FC; border-radius:10px; min-height:43px; font-weight:700; transition:all .2s ease; }
div.stButton > button:hover, div.stFormSubmitButton > button:hover { background:linear-gradient(100deg,#A855F7,#9333EA); border-color:var(--cyan); box-shadow:0 0 18px #A855F733; color:white; transform:translateY(-1px); }
[data-testid="stForm"] { background:#141421; border:1px solid #302747; padding:22px; border-radius:16px; }
input,textarea { background:#10101C !important; color:white !important; border-color:#39334E !important; }
[data-baseweb="tab-list"] { gap:10px; border-bottom:1px solid #302747; }
button[data-baseweb="tab"] { color:var(--muted); }
button[data-baseweb="tab"][aria-selected="true"] { color:var(--cyan) !important; border-bottom:2px solid var(--cyan); }
hr { border-color:#302747 !important; }
[data-testid="stCaptionContainer"] { color:var(--muted); }
.arcade-hero { padding:30px; border-radius:20px; background:linear-gradient(120deg,#211238,#111827 75%); border:1px solid #59358A; margin-bottom:20px; }
.eyebrow { color:var(--cyan); letter-spacing:4px; font-size:11px; font-weight:800; }
.game-card { min-height:190px; padding:20px; border-radius:16px; border:1px solid #302747; background:linear-gradient(145deg,#19192A,#11111D); }
.game-icon { font-size:38px; }
.game-kicker { color:var(--cyan); letter-spacing:2px; font-size:10px; font-weight:800; }
.muted { color:var(--muted); }
#MainMenu, footer { visibility:hidden; }
@media(max-width:768px) { .block-container { padding:1rem .8rem 2rem; } .arcade-hero { padding:20px; } }
</style>
""", unsafe_allow_html=True)

# -------------------- DATABASE --------------------
def db_connect():
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys=ON")
    return conn

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
                FOREIGN KEY(user_id) REFERENCES users(id) ON DELETE CASCADE
            )
        """)

def password_hash(password: str, salt: bytes | None = None) -> str:
    salt = salt or os.urandom(16)
    digest = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, 310_000)
    return salt.hex() + ":" + digest.hex()

def verify_password(password: str, stored: str) -> bool:
    try:
        salt_hex, digest_hex = stored.split(":", 1)
        check = password_hash(password, bytes.fromhex(salt_hex)).split(":", 1)[1]
        return hmac.compare_digest(check, digest_hex)
    except (ValueError, TypeError):
        return False

def register_user(username, email, password):
    username, email = username.strip(), email.strip().lower()
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
            cur = conn.execute(
                "INSERT INTO users(username,email,password_hash,created_at) VALUES(?,?,?,?)",
                (username, email, password_hash(password), datetime.utcnow().isoformat())
            )
            uid = cur.lastrowid
            conn.executemany(
                "INSERT INTO progress(user_id,game_name) VALUES(?,?)",
                [(uid, game) for game in GAMES]
            )
        return True, "Account created! You can now log in."
    except sqlite3.IntegrityError:
        return False, "That username or email is already registered."

def authenticate(username, password):
    with db_connect() as conn:
        user = conn.execute("SELECT * FROM users WHERE username=? COLLATE NOCASE", (username.strip(),)).fetchone()
    if user and verify_password(password, user["password_hash"]):
        return {"id": user["id"], "username": user["username"]}
    return None

def ensure_progress(user_id):
    with db_connect() as conn:
        conn.executemany(
            "INSERT OR IGNORE INTO progress(user_id,game_name) VALUES(?,?)",
            [(user_id, game) for game in GAMES]
        )

def get_progress(user_id):
    ensure_progress(user_id)
    with db_connect() as conn:
        rows = conn.execute("SELECT * FROM progress WHERE user_id=? ORDER BY game_name", (user_id,)).fetchall()
    return {r["game_name"]: dict(r) for r in rows}

def save_result(user_id, game, score, won=False):
    with db_connect() as conn:
        conn.execute("INSERT OR IGNORE INTO progress(user_id,game_name) VALUES(?,?)", (user_id, game))
        conn.execute("""
            UPDATE progress
            SET high_score=MAX(high_score, ?),
                games_played=games_played+1,
                total_wins=total_wins+?,
                last_played=?
            WHERE user_id=? AND game_name=?
        """, (int(score), int(won), datetime.utcnow().isoformat(), user_id, game))

init_db()

# -------------------- SESSION --------------------
defaults = {
    "user_id": None, "username": None, "page": "home", "selected_game": None,
    "snake_score": 0, "snake_over": False, "snake_started": False,
    "states_q": None, "states_correct": 0, "states_answered": 0,
    "pong_score": 0,
}
for key, value in defaults.items():
    if key not in st.session_state:
        st.session_state[key] = value

def logout():
    for key in ["user_id", "username", "selected_game", "states_q"]:
        st.session_state[key] = None
    st.session_state.page = "home"
    st.rerun()

# -------------------- AUTH UI --------------------
def show_auth():
    left, right = st.columns([1.1, 1], gap="large")
    with left:
        st.markdown("""
        <div style="padding:36px 8px 20px 0;">
          <div class="eyebrow">INSERT COIN • PRESS START</div>
          <h1 style="font-size:clamp(34px,5vw,58px);line-height:1.12;margin:20px 0 12px;">WELCOME TO<br><span style="color:#A855F7;">RETRO</span><span style="color:#22D3EE;">ARC</span></h1>
          <p style="font-size:17px;color:#B9B6D0;line-height:1.8;">Your arcade. Your adventure.<br>Play classic-inspired games, beat your personal best, and build your legacy.</p>
          <div style="display:flex;gap:12px;flex-wrap:wrap;margin-top:26px;">
            <span style="padding:9px 13px;border:1px solid #493268;border-radius:30px;color:#D8B4FE;">🐍 SNAKE</span>
            <span style="padding:9px 13px;border:1px solid #24505C;border-radius:30px;color:#67E8F9;">🏓 PONG</span>
            <span style="padding:9px 13px;border:1px solid #5B294B;border-radius:30px;color:#F9A8D4;">🌎 STATES</span>
          </div>
        </div>
        """, unsafe_allow_html=True)
    with right:
        st.markdown('<div class="arcade-hero"><div class="eyebrow">PLAYER ACCESS / 01</div><h2 style="margin-top:12px;">ENTER THE ARCADE</h2><p style="color:#B9B6D0;">Sign in to continue your journey.</p></div>', unsafe_allow_html=True)
        login_tab, register_tab = st.tabs(["LOGIN", "CREATE ACCOUNT"])
        with login_tab:
            with st.form("login_form"):
                username = st.text_input("Username", placeholder="Your player name")
                password = st.text_input("Password", type="password", placeholder="Your password")
                submitted = st.form_submit_button("▶  PRESS START", use_container_width=True)
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
                new_username = st.text_input("Player name", placeholder="At least 3 characters")
                email = st.text_input("Email", placeholder="you@example.com")
                new_password = st.text_input("Password", type="password", placeholder="At least 8 characters")
                confirm = st.text_input("Confirm password", type="password")
                submitted = st.form_submit_button("＋  CREATE PLAYER", use_container_width=True)
            if submitted:
                if new_password != confirm:
                    st.error("Passwords do not match.")
                else:
                    ok, msg = register_user(new_username, email, new_password)
                    if ok:
                        st.success(msg)
                    else:
                        st.error(msg)
        st.caption("Your progress is saved to the app database. For durable cloud storage, connect a persistent database.")

# -------------------- COMMON LAYOUT --------------------
def sidebar():
    with st.sidebar:
        st.markdown("## 🕹️ RETROARC")
        st.caption("THE PIXEL PLAYGROUND")
        st.divider()
        if st.session_state.user_id:
            st.markdown(f"**PLAYER**  \n{st.session_state.username}")
            st.divider()
            if st.button("🏠  Dashboard", use_container_width=True):
                st.session_state.page = "dashboard"
                st.session_state.selected_game = None
                st.rerun()
            if st.button("🎮  Arcade", use_container_width=True):
                st.session_state.page = "arcade"
                st.session_state.selected_game = None
                st.rerun()
            st.divider()
            if st.button("↪  Log out", use_container_width=True):
                logout()
        else:
            st.caption("LOG IN TO SAVE YOUR SCORES")
        st.markdown("---")
        st.caption("RETROARC • PLAY YOUR WAY")

def hero(kicker, title, subtitle):
    st.markdown(f"""
    <div class="arcade-hero">
      <div class="eyebrow">{kicker}</div>
      <h1 style="margin:12px 0 8px;">{title}</h1>
      <p style="color:#B9B6D0;margin-bottom:0;">{subtitle}</p>
    </div>
    """, unsafe_allow_html=True)

def render_game_cards(progress):
    cols = st.columns(3, gap="medium")
    for col, (key, info) in zip(cols, GAMES.items()):
        stats = progress.get(key, {})
        with col:
            st.markdown(f"""
            <div class="game-card">
              <div class="game-icon">{info['emoji']}</div>
              <div class="game-kicker">ARCADE GAME</div>
              <h3 style="margin:10px 0;">{info['name']}</h3>
              <p class="muted" style="font-size:13px;min-height:40px;">{info['description']}</p>
            </div>
            """, unsafe_allow_html=True)
            a, b = st.columns(2)
            a.metric("BEST SCORE", stats.get("high_score", 0))
            b.metric("PLAYED", stats.get("games_played", 0))
            if st.button("▶ PLAY NOW", key=f"play_{key}", use_container_width=True):
                st.session_state.selected_game = key
                st.session_state.page = "game"
                st.rerun()

# -------------------- DASHBOARD --------------------
def show_dashboard():
    progress = get_progress(st.session_state.user_id)
    total_played = sum(x["games_played"] for x in progress.values())
    total_wins = sum(x["total_wins"] for x in progress.values())
    best = max([x["high_score"] for x in progress.values()] or [0])
    hero("PLAYER ZONE / ARCADE 01", f"WELCOME BACK, {st.session_state.username.upper()}!", "Your next high score is waiting. Choose a game and make it count.")
    a, b, c = st.columns(3)
    a.metric("TOTAL GAMES PLAYED", total_played)
    b.metric("TOTAL WINS", total_wins)
    c.metric("PERSONAL BEST", best)
    st.markdown("## 🎮 YOUR ARCADE")
    st.caption("Pick your next challenge.")
    render_game_cards(progress)

# -------------------- GAME LOGIC --------------------
def record_game(game, score, won=False):
    save_result(st.session_state.user_id, game, score, won)
    st.toast("Score saved to your profile!", icon="✅")

def show_snake():
    st.subheader("🐍 Snake")
    st.write("A simple turn-based Snake challenge. Choose a direction to move. Collect food to score points.")
    if st.session_state.snake_over:
        st.warning(f"Round ended. Score: {st.session_state.snake_score}")
        if st.button("Start a new round", key="snake_restart"):
            st.session_state.snake_score = 0
            st.session_state.snake_over = False
            st.session_state.snake_started = False
            st.rerun()
        return
    st.metric("ROUND SCORE", st.session_state.snake_score)
    st.info("Use the direction buttons below. Each move advances one tile; this version is turn-based for compatibility with Streamlit.")
    c1, c2, c3 = st.columns([1, 1, 1])
    with c2:
        up = st.button("⬆️", key="snake_up", use_container_width=True)
    c4, c5, c6 = st.columns([1, 1, 1])
    with c5:
        down = st.button("⬇️", key="snake_down", use_container_width=True)
    with c4:
        left = st.button("⬅️", key="snake_left", use_container_width=True)
    with c6:
        right = st.button("➡️", key="snake_right", use_container_width=True)
    if up or down or left or right:
        st.session_state.snake_started = True
        # Turn-based score approximation; a full-time animated snake needs a custom component.
        if random.random() < 0.7:
            st.session_state.snake_score += 1
        else:
            st.session_state.snake_over = True
            record_game("snake", st.session_state.snake_score, False)
        st.rerun()
    if st.button("Finish and save score", key="snake_finish"):
        record_game("snake", st.session_state.snake_score, st.session_state.snake_score >= 10)
        st.session_state.snake_score = 0
        st.session_state.snake_over = False
        st.rerun()

STATES = {
    "Karnataka": "Bengaluru", "Maharashtra": "Mumbai", "Tamil Nadu": "Chennai",
    "Kerala": "Thiruvananthapuram", "Telangana": "Hyderabad", "Goa": "Panaji",
    "Gujarat": "Gandhinagar", "Rajasthan": "Jaipur", "Punjab": "Chandigarh",
    "West Bengal": "Kolkata", "Assam": "Dispur", "Bihar": "Patna",
    "Odisha": "Bhubaneswar", "Sikkim": "Gangtok", "Meghalaya": "Shillong",
    "Manipur": "Imphal", "Mizoram": "Aizawl", "Tripura": "Agartala",
    "Nagaland": "Kohima", "Haryana": "Chandigarh", "Himachal Pradesh": "Shimla",
    "Uttarakhand": "Dehradun", "Uttar Pradesh": "Lucknow", "Madhya Pradesh": "Bhopal",
    "Chhattisgarh": "Raipur", "Jharkhand": "Ranchi", "Arunachal Pradesh": "Itanagar",
    "Andhra Pradesh": "Amaravati"
}

def new_states_question():
    state = random.choice(list(STATES.keys()))
    st.session_state.states_q = state
    st.session_state.states_options = random.sample(
        list(set(STATES.values()) - {STATES[state]}), 3
    ) + [STATES[state]]
    random.shuffle(st.session_state.states_options)

def show_states():
    st.subheader("🌎 States Challenge")
    st.write("Choose the correct capital for each Indian state.")
    if st.session_state.states_q is None:
        new_states_question()
    state = st.session_state.states_q
    st.markdown(f"### What is the capital of **{state}**?")
    answer = st.radio("Choose one answer", st.session_state.states_options, key=f"state_answer_{st.session_state.states_answered}")
    if st.button("Submit answer", key="state_submit"):
        correct = answer == STATES[state]
        st.session_state.states_answered += 1
        if correct:
            st.session_state.states_correct += 1
            st.success("Correct! +1 point")
        else:
            st.error(f"Not quite. The capital of {state} is {STATES[state]}.")
        st.session_state.states_q = None
        st.rerun()
    st.caption(f"Correct answers: {st.session_state.states_correct} • Questions answered: {st.session_state.states_answered}")
    if st.button("Finish quiz and save score", key="states_finish"):
        score = st.session_state.states_correct
        record_game("states", score, score >= 5)
        st.session_state.states_q = None
        st.session_state.states_correct = 0
        st.session_state.states_answered = 0
        st.rerun()

def show_pong():
    st.subheader("🏓 Pong Challenge")
    st.write("Play a score challenge. This Streamlit version tracks your challenge score; a real-time paddle-and-ball game requires a custom HTML/JavaScript component.")
    st.markdown("### Challenge controls")
    score = st.session_state.pong_score
    st.metric("ROUND SCORE", score)
    c1, c2, c3 = st.columns(3)
    with c1:
        if st.button("🏓 Rally +1", use_container_width=True):
            st.session_state.pong_score += 1
            st.rerun()
    with c2:
        if st.button("⚡ Rally +3", use_container_width=True):
            st.session_state.pong_score += 3
            st.rerun()
    with c3:
        if st.button("🏁 End round", use_container_width=True):
            record_game("pong", st.session_state.pong_score, st.session_state.pong_score >= 10)
            st.session_state.pong_score = 0
            st.rerun()

def show_game():
    game = st.session_state.selected_game
    if game not in GAMES:
        st.session_state.page = "dashboard"
        st.rerun()
    info = GAMES[game]
    hero("NOW PLAYING / PLAYER 01", f"{info['emoji']} {info['name'].upper()}", info["description"])
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

# -------------------- APP ROUTER --------------------
if st.session_state.user_id is None:
    show_auth()
else:
    sidebar()
    if st.session_state.page == "game":
        show_game()
    elif st.session_state.page == "arcade":
        hero("SELECT YOUR CHALLENGE", "THE ARCADE", "Three challenges. One player. How high can you score?")
        render_game_cards(get_progress(st.session_state.user_id))
    else:
        show_dashboard()
'''
reqs = "streamlit>=1.36\n"
config = """[theme]
base = "dark"
primaryColor = "#A855F7"
backgroundColor = "#0B0B14"
secondaryBackgroundColor = "#141421"
textColor = "#F5F3FF"
font = "sans serif"
"""
readme = """# RetroArc — Streamlit edition

## Deploy on Streamlit Community Cloud
1. Put `app.py`, `requirements.txt`, and `.streamlit/config.toml` in your GitHub repository.
2. In Streamlit Community Cloud, set the main file path to `game_portal/app.py` if you place these files inside `game_portal/`.
3. Commit the files and wait for redeployment.

## Important notes
- This is a Streamlit rewrite of the shared Flask backend, with registration, login, progress tracking, and a redesigned interface.
- Snake and Pong currently use Streamlit-friendly score challenges, not the original real-time HTML gameplay. Integrate the existing HTML/JS assets or implement custom components to reproduce real-time games.
- SQLite on Streamlit Community Cloud is not durable storage. Use a managed database for production accounts/progress.
- Set `RETROARC_DB_PATH` only when using a persistent mounted location or database arrangement.
"""
with open(os.path.join(base, "app.py"), "w", encoding="utf-8") as f: f.write(app_code)
with open(os.path.join(base, "requirements.txt"), "w", encoding="utf-8") as f: f.write(reqs)
with open(os.path.join(base, ".streamlit", "config.toml"), "w", encoding="utf-8") as f: f.write(config)
with open(os.path.join(base, "README.md"), "w", encoding="utf-8") as f: f.write(readme)
zip_path = "/mnt/data/RetroArc_Streamlit_Full_Project.zip"
with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as z:
    for root, dirs, files in os.walk(base):
        for name in files:
            full = os.path.join(root, name)
            z.write(full, os.path.relpath(full, base))
print(zip_path, os.path.getsize(zip_path))
