from flask import Flask, render_template, request, redirect, url_for, session, jsonify
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key-change-this-in-production'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///retroarc.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# Database Models
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(200), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    progress = db.relationship('GameProgress', backref='user', lazy=True)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class GameProgress(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    game_name = db.Column(db.String(50), nullable=False)  # 'pong', 'snake'
    high_score = db.Column(db.Integer, default=0)
    games_played = db.Column(db.Integer, default=0)
    total_wins = db.Column(db.Integer, default=0)
    last_played = db.Column(db.DateTime, default=datetime.utcnow)

# Routes
@app.route('/')
def index():
    if 'user_id' in session:
        return redirect(url_for('dashboard'))
    return render_template('index.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        
        if User.query.filter_by(username=username).first():
            return render_template('register.html', error='Username already exists')
        
        if User.query.filter_by(email=email).first():
            return render_template('register.html', error='Email already registered')
        
        user = User(username=username, email=email)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()
        
        # Create initial progress entries for all games
        for game in ['pong', 'snake', 'states']:
            progress = GameProgress(user_id=user.id, game_name=game)
            db.session.add(progress)
        db.session.commit()
        
        session['user_id'] = user.id
        session['username'] = user.username
        return redirect(url_for('dashboard'))
    
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        user = User.query.filter_by(username=username).first()
        
        if user and user.check_password(password):
            session['user_id'] = user.id
            session['username'] = user.username
            return redirect(url_for('dashboard'))
        
        return render_template('login.html', error='Invalid username or password')
    
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))

@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    user = User.query.get(session['user_id'])
    
    # Ensure all game progress entries exist for this user
    all_games = ['pong', 'snake', 'states']
    existing_progress = GameProgress.query.filter_by(user_id=user.id).all()
    existing_games = {p.game_name for p in existing_progress}
    
    # Create missing game progress entries
    for game in all_games:
        if game not in existing_games:
            new_progress = GameProgress(user_id=user.id, game_name=game)
            db.session.add(new_progress)
    db.session.commit()
    
    # Reload progress after ensuring all entries exist
    progress = GameProgress.query.filter_by(user_id=user.id).all()
    
    game_stats = {}
    for p in progress:
        game_stats[p.game_name] = {
            'high_score': p.high_score,
            'games_played': p.games_played,
            'total_wins': p.total_wins,
            'last_played': p.last_played
        }
    
    return render_template('dashboard.html', username=user.username, stats=game_stats)

@app.route('/play/<game_name>')
def play_game(game_name):
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    if game_name not in ['pong', 'snake', 'states']:
        return redirect(url_for('dashboard'))
    
    return render_template(f'play_{game_name}.html', game_name=game_name)

@app.route('/api/update_progress', methods=['POST'])
def update_progress():
    if 'user_id' not in session:
        return jsonify({'error': 'Not authenticated'}), 401
    
    data = request.get_json()
    game_name = data.get('game_name')
    score = data.get('score', 0)
    won = data.get('won', False)
    
    progress = GameProgress.query.filter_by(
        user_id=session['user_id'], 
        game_name=game_name
    ).first()
    
    if progress:
        progress.games_played += 1
        if score > progress.high_score:
            progress.high_score = score
        if won:
            progress.total_wins += 1
        progress.last_played = datetime.utcnow()
        db.session.commit()
        
        return jsonify({'success': True, 'high_score': progress.high_score})
    
    return jsonify({'error': 'Progress not found'}), 404

@app.route('/api/get_progress/<game_name>')
def get_progress(game_name):
    if 'user_id' not in session:
        return jsonify({'error': 'Not authenticated'}), 401
    
    progress = GameProgress.query.filter_by(
        user_id=session['user_id'], 
        game_name=game_name
    ).first()
    
    # If progress doesn't exist, create it
    if not progress:
        progress = GameProgress(user_id=session['user_id'], game_name=game_name)
        db.session.add(progress)
        db.session.commit()
    
    return jsonify({
        'high_score': progress.high_score,
        'games_played': progress.games_played,
        'total_wins': progress.total_wins
    })

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True, host='0.0.0.0', port=5000)
