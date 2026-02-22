# RetroArc - Multi-Game Website with User Authentication

A web-based gaming platform featuring classic games (Pong and Snake) with user authentication, progress tracking, and persistent high scores.

## Features

- **User Authentication**: Register and login system with secure password hashing
- **Multiple Games**: Play Pong and Snake directly in your browser
- **Progress Tracking**: Track high scores, games played, and wins for each game
- **Responsive Design**: Beautiful, modern UI that works on all devices
- **Real-time Statistics**: View your gaming statistics on the dashboard

## Games Included

### 1. Pong 🏓
- Classic two-player paddle game
- Controls: W/S for left paddle, Arrow keys for right paddle
- First to 6 points wins

### 2. Snake 🐍
- Classic snake game where you eat food to grow
- Controls: Arrow keys to move
- Avoid walls and your own tail

## Installation

1. **Navigate to the game portal directory:**
   ```powershell
   cd "c:\Users\dhanv\OneDrive\Desktop\bhakthi desk\bhakthi python\retroarc"
   ```

2. **Create a virtual environment (recommended):**
   ```powershell
   python -m venv venv
   .\venv\Scripts\Activate.ps1
   ```

3. **Install dependencies:**
   ```powershell
   pip install -r requirements.txt
   ```

4. **Run the application:**
   ```powershell
   python app.py
   ```

5. **Open your browser and visit:**
   ```
   http://localhost:5000
   ```

## Project Structure

```
etroarc/
├── app.py                      # Main Flask application
├── requirements.txt            # Python dependencies
├── retroarc.db                # SQLite database (created automatically)
├── static/
│   ├── css/
│   │   └── style.css          # Styling for the website
│   └── js/
│       ├── pong.js            # Pong game logic
│       └── snake.js           # Snake game logic
└── templates/
    ├── base.html              # Base template
    ├── index.html             # Landing page
    ├── login.html             # Login page
    ├── register.html          # Registration page
    ├── dashboard.html         # Game selection dashboard
    ├── play_pong.html         # Pong game page
    └── play_snake.html        # Snake game page
```

## How to Use

1. **Register an Account:**
   - Click "Create Account" on the home page
   - Fill in your username, email, and password
   - Click "Register"

2. **Login:**
   - Enter your username and password
   - Click "Login"

3. **Select a Game:**
   - From your dashboard, click on either "Play Pong" or "Play Snake"
   - Your statistics will be displayed for each game

4. **Play Games:**
   - Follow the on-screen controls
   - Your progress is automatically saved
   - High scores are tracked and displayed

## Database Schema

### User Table
- id: Primary key
- username: Unique username
- email: Unique email address
- password_hash: Hashed password
- created_at: Account creation timestamp

### GameProgress Table
- id: Primary key
- user_id: Foreign key to User
- game_name: Name of the game (pong/snake)
- high_score: User's highest score
- games_played: Total games played
- total_wins: Total wins
- last_played: Last play timestamp

## API Endpoints

- `GET /`: Home page
- `GET/POST /register`: User registration
- `GET/POST /login`: User login
- `GET /logout`: User logout
- `GET /dashboard`: User dashboard with game selection
- `GET /play/<game_name>`: Play specific game
- `POST /api/update_progress`: Update game progress
- `GET /api/get_progress/<game_name>`: Get game progress

## Security Features

- Password hashing using Werkzeug security
- Session-based authentication
- CSRF protection through Flask
- SQL injection prevention through SQLAlchemy ORM

## Future Enhancements

- Add more games
- Implement leaderboards
- Add multiplayer functionality
- Mobile app version
- Social features (friends, challenges)
- Achievement system

## Troubleshooting

**Port already in use:**
- Change the port in `app.py`: `app.run(debug=True, host='0.0.0.0', port=5001)`

**Database errors:**
- Delete `game_portal.db` and restart the application to recreate the database

**Module not found:**
- Make sure you've activated the virtual environment and installed requirements

## Credits

Original games concept based on:
- Pong game implementation
- Snake game implementation

Developed by: Bhakthi
Date: February 2026

## License

This project is for educational purposes.
