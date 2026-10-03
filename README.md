# 🎮 RetroArc – Multi-Game Website with User Authentication

**RetroArc** is a web-based gaming platform built with Python and Flask that brings classic arcade games into the browser. It features user authentication, individual gaming statistics, progress tracking, and persistent high scores, providing users with a personalized gaming experience.

## ✨ Features

* **User Authentication:** User registration and login with password hashing.
* **Classic Arcade Games:** Play Pong and Snake directly in your browser.
* **Progress Tracking:** Track games played, high scores, and wins for each game.
* **Personalized Dashboard:** View gaming statistics and choose games from a central dashboard.
* **Persistent Data Storage:** Store user accounts and game progress in an SQLite database.
* **Responsive Interface:** Modern interface designed to work across different screen sizes.
* **Session Management:** Maintain authenticated user sessions while navigating the platform.

## 🕹️ Games Included

### 1. Pong 🏓

A classic paddle game where players compete to score points against each other.

**Controls**

* **Left paddle:** `W` to move up and `S` to move down
* **Right paddle:** `↑` to move up and `↓` to move down
* **Winning condition:** First player to reach 6 points wins.

### 2. Snake 🐍

A classic snake game where players guide a growing snake to collect food while avoiding collisions.

**Controls**

* `↑` – Move up
* `↓` – Move down
* `←` – Move left
* `→` – Move right

**Objective:** Eat food to grow longer while avoiding the walls and your own tail.

## 🛠️ Tech Stack

| Technology | Purpose                                 |
| ---------- | --------------------------------------- |
| Python     | Backend application logic               |
| Flask      | Web framework and routing               |
| HTML5      | Web page structure                      |
| CSS3       | Styling and responsive interface        |
| JavaScript | Browser-based game logic                |
| SQLite     | Database for user accounts and progress |
| SQLAlchemy | Database ORM                            |
| Werkzeug   | Password hashing and security utilities |

## 📂 Project Structure

```text
retroarc/
├── app.py                      # Main Flask application
├── requirements.txt            # Python dependencies
├── retroarc.db                 # SQLite database (created automatically)
├── static/
│   ├── css/
│   │   └── style.css           # Website styling
│   └── js/
│       ├── pong.js             # Pong game logic
│       └── snake.js            # Snake game logic
└── templates/
    ├── base.html               # Base HTML template
    ├── index.html              # Landing page
    ├── login.html              # Login page
    ├── register.html           # Registration page
    ├── dashboard.html          # Game selection and statistics
    ├── play_pong.html          # Pong game interface
    └── play_snake.html         # Snake game interface
```

## ⚙️ Installation and Setup

Follow these steps to run RetroArc locally.

### Prerequisites

* Python 3.9 or a compatible version
* pip (Python package installer)
* A modern web browser
* Git (optional, for cloning the repository)

### 1. Clone the Repository

```bash
git clone <YOUR_GITHUB_REPOSITORY_URL>
cd retroarc
```

Replace `<YOUR_GITHUB_REPOSITORY_URL>` with your repository's actual URL. If you have already downloaded the project, open a terminal in the project directory instead.

### 2. Create a Virtual Environment

**Windows PowerShell:**

```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

**Windows Command Prompt:**

```cmd
python -m venv venv
venv\Scripts\activate.bat
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Start the Application

```bash
python app.py
```

### 5. Open RetroArc

Open your browser and navigate to:

```text
http://localhost:5000
```

The SQLite database is expected to be created automatically when the application initializes, according to its implementation.

## 🚀 How to Use

1. **Create an account:** Open the home page, select the registration option, and enter your username, email, and password.
2. **Log in:** Sign in using your registered credentials.
3. **Open the dashboard:** Choose between Pong and Snake.
4. **Start playing:** Follow the controls displayed on the game page.
5. **Track your progress:** View your saved high scores, games played, and wins on the dashboard.

## 🗄️ Database Schema

RetroArc uses SQLite to store user information and game progress.

### User Table

| Field           | Description                            |
| --------------- | -------------------------------------- |
| `id`            | Unique user identifier and primary key |
| `username`      | Unique username                        |
| `email`         | Unique email address                   |
| `password_hash` | Hashed password                        |
| `created_at`    | Account creation timestamp             |

### GameProgress Table

| Field          | Description                         |
| -------------- | ----------------------------------- |
| `id`           | Unique progress record identifier   |
| `user_id`      | Foreign key referencing the user    |
| `game_name`    | Game identifier (`pong` or `snake`) |
| `high_score`   | Highest recorded score              |
| `games_played` | Total number of games played        |
| `total_wins`   | Total recorded wins                 |
| `last_played`  | Timestamp of the last play session  |

## 🔌 Application Routes and API Endpoints

| Method        | Endpoint                        | Description                              |
| ------------- | ------------------------------- | ---------------------------------------- |
| `GET`         | `/`                             | Displays the home page                   |
| `GET`, `POST` | `/register`                     | Displays and processes user registration |
| `GET`, `POST` | `/login`                        | Displays and processes user login        |
| `GET`         | `/logout`                       | Logs out the current user                |
| `GET`         | `/dashboard`                    | Displays the user's dashboard            |
| `GET`         | `/play/<game_name>`             | Opens the selected game                  |
| `POST`        | `/api/update_progress`          | Updates game progress                    |
| `GET`         | `/api/get_progress/<game_name>` | Retrieves progress for a specific game   |

## 🔐 Security Features

The project includes the following security-related mechanisms, as described in its implementation:

* **Password Hashing:** Uses Werkzeug security utilities to hash passwords instead of storing plain-text passwords.
* **Session-Based Authentication:** Uses sessions to maintain user login state.
* **Database ORM:** Uses SQLAlchemy to interact with the database and reduce the need for manually constructed SQL queries.
* **CSRF Protection:** The project documentation specifies CSRF protection; verify that the relevant protection is configured and enabled in the application.

**Security note:** Before deploying publicly, review session configuration, input validation, authorization checks, CSRF protection, and production settings. Do not expose development debug mode on a public server.

## 🔮 Future Enhancements

Potential improvements for future versions include:

* Global and game-specific leaderboards.
* Additional classic arcade games.
* Multiplayer gameplay.
* Achievement badges and player milestones.
* Friends, challenges, and social features.
* Improved mobile controls and accessibility.
* A dedicated mobile application.

## 🧰 Troubleshooting

### Port Already in Use

If port `5000` is occupied, change the port in the application's run configuration:

```python
app.run(debug=True, host="0.0.0.0", port=5001)
```

Then open `http://localhost:5001`.

**Note:** Use `debug=False` when running in a production environment.

### Missing Modules

If you encounter a `ModuleNotFoundError`, activate the virtual environment and reinstall the dependencies:

```bash
pip install -r requirements.txt
```

### Database Errors

Check the database configuration and initialization code in `app.py`. Back up any important data before deleting or recreating the database.

### Virtual Environment Issues

Ensure that the virtual environment is activated before installing dependencies or starting the application.

## 👩‍💻 Developer

**Bhakthi Kanabar**
Computer Science and Engineering Student

* **GitHub:** [bhakthikanabar-tech](https://github.com/bhakthikanabar-tech)
* **LinkedIn:** [Bhakthi Kanabar](https://linkedin.com/in/bhakthi-kanabar-3b597428a)

## 📄 License

This project was developed for educational purposes. No specific open-source license is specified. Add a `LICENSE` file if you intend to distribute the project under a particular license.

---

**RetroArc – Play Classic. Track Progress. Keep Beating Your High Score!** 🎮
