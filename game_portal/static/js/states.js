// US States Game Implementation
const canvas = document.getElementById('gameCanvas');
const ctx = canvas.getContext('2d');
const stateInput = document.getElementById('stateInput');
const inputContainer = document.getElementById('inputContainer');
const startBtn = document.getElementById('startBtn');
const giveUpBtn = document.getElementById('giveUpBtn');

// Game state
let gameStarted = false;
let gameOver = false;
let score = 0;
let highScore = 0;
let startTime = 0;
let timerInterval = null;

// States data
let statesData = [];
let guessedStates = new Set();

// ========================================
// GAME SOUND EFFECTS
// ========================================

let audioContext;

function playSound(type) {
    try {
        if (!audioContext) {
            audioContext = new (
                window.AudioContext || window.webkitAudioContext
            )();
        }

        if (audioContext.state === 'suspended') {
            audioContext.resume();
        }

        const oscillator = audioContext.createOscillator();
        const gainNode = audioContext.createGain();

        oscillator.connect(gainNode);
        gainNode.connect(audioContext.destination);

        const now = audioContext.currentTime;

        if (type === 'correct') {
            // Cheerful two-note sound for a correct answer.
            oscillator.type = 'sine';
            oscillator.frequency.setValueAtTime(660, now);
            oscillator.frequency.setValueAtTime(880, now + 0.1);

            gainNode.gain.setValueAtTime(0.16, now);
            gainNode.gain.exponentialRampToValueAtTime(
                0.01,
                now + 0.25
            );

            oscillator.start(now);
            oscillator.stop(now + 0.25);

        } else if (type === 'wrong') {
            // Low, buzzy sound for an incorrect answer.
            oscillator.type = 'square';
            oscillator.frequency.setValueAtTime(180, now);
            oscillator.frequency.setValueAtTime(110, now + 0.15);

            gainNode.gain.setValueAtTime(0.10, now);
            gainNode.gain.exponentialRampToValueAtTime(
                0.01,
                now + 0.3
            );

            oscillator.start(now);
            oscillator.stop(now + 0.3);
        }

    } catch (error) {
        console.warn('Could not play sound:', error);
    }
}

// ========================================
// LOAD STATES DATA
// ========================================

async function loadStatesData() {
    try {
        const response = await fetch('/static/data/states.csv');
        const text = await response.text();
        const lines = text.trim().split('\n');

        // Skip header
        for (let i = 1; i < lines.length; i++) {
            const [state, x, y] = lines[i].split(',');

            statesData.push({
                name: state,
                x: parseFloat(x) + 400,
                y: parseFloat(y) + 300
            });
        }

    } catch (error) {
        console.error('Error loading states data:', error);
    }
}

// ========================================
// LOAD HIGH SCORE
// ========================================

async function loadHighScore() {
    try {
        const response = await fetch('/api/get_progress/states');
        const data = await response.json();

        if (data.high_score) {
            highScore = data.high_score;
            document.getElementById('highScore').textContent =
                `${highScore}/50`;
        }

    } catch (error) {
        console.error('Error loading high score:', error);
    }
}

// ========================================
// UPDATE PROGRESS
// ========================================

async function updateProgress(finalScore, won) {
    try {
        await fetch('/api/update_progress', {
            method: 'POST',

            headers: {
                'Content-Type': 'application/json'
            },

            body: JSON.stringify({
                game_name: 'states',
                score: finalScore,
                won: won
            })
        });

    } catch (error) {
        console.error('Error updating progress:', error);
    }
}

// ========================================
// DRAW FUNCTIONS
// ========================================

function drawText(
    text,
    x,
    y,
    color,
    size = 14,
    align = 'center'
) {
    ctx.fillStyle = color;
    ctx.font = `bold ${size}px Arial`;
    ctx.textAlign = align;
    ctx.fillText(text, x, y);
}

function drawMap() {
    // Clear canvas with white background.
    ctx.fillStyle = '#ffffff';
    ctx.fillRect(0, 0, canvas.width, canvas.height);

    // Draw all unguessed state locations as gray dots.
    statesData.forEach(state => {
        if (!guessedStates.has(state.name)) {
            ctx.fillStyle = '#cccccc';

            ctx.beginPath();
            ctx.arc(state.x, state.y, 3, 0, Math.PI * 2);
            ctx.fill();
        }
    });

    // Draw guessed states.
    guessedStates.forEach(stateName => {
        const state = statesData.find(
            s => s.name === stateName
        );

        if (state) {
            // Green dot for guessed state.
            ctx.fillStyle = '#4CAF50';

            ctx.beginPath();
            ctx.arc(state.x, state.y, 5, 0, Math.PI * 2);
            ctx.fill();

            // Draw state name with shadow.
            ctx.shadowColor = 'rgba(255, 255, 255, 0.8)';
            ctx.shadowBlur = 3;

            drawText(
                state.name,
                state.x,
                state.y - 8,
                '#000',
                11
            );

            ctx.shadowBlur = 0;
        }
    });

    // Start screen.
    if (!gameStarted && !gameOver) {
        ctx.fillStyle = 'rgba(255, 255, 255, 0.9)';
        ctx.fillRect(0, 0, canvas.width, canvas.height);

        drawText(
            'Click "Start Game" to begin!',
            canvas.width / 2,
            canvas.height / 2,
            '#667eea',
            28
        );

        drawText(
            'Type state names to place them on the map',
            canvas.width / 2,
            canvas.height / 2 + 40,
            '#333',
            18
        );
    }

    // Game-over screen.
    if (gameOver) {
        ctx.fillStyle = 'rgba(0, 0, 0, 0.85)';
        ctx.fillRect(0, 0, canvas.width, canvas.height);

        drawText(
            'GAME OVER!',
            canvas.width / 2,
            canvas.height / 2 - 60,
            '#fff',
            40
        );

        drawText(
            `You got ${score} out of 50 states!`,
            canvas.width / 2,
            canvas.height / 2 - 10,
            '#fff',
            24
        );

        if (score === 50) {
            drawText(
                'Perfect Score!',
                canvas.width / 2,
                canvas.height / 2 + 30,
                '#ffd700',
                28
            );
        } else {
            const percentage = Math.round((score / 50) * 100);

            drawText(
                `${percentage}% Complete`,
                canvas.width / 2,
                canvas.height / 2 + 30,
                '#4CAF50',
                20
            );
        }
    }
}

// ========================================
// TIMER
// ========================================

function startTimer() {
    startTime = Date.now();

    // Prevent multiple timer intervals.
    stopTimer();

    startTime = Date.now();

    timerInterval = setInterval(() => {
        const elapsed = Math.floor(
            (Date.now() - startTime) / 1000
        );

        const minutes = Math.floor(elapsed / 60);
        const seconds = elapsed % 60;

        document.getElementById('timer').textContent =
            `${minutes}:${seconds.toString().padStart(2, '0')}`;

    }, 1000);
}

function stopTimer() {
    if (timerInterval) {
        clearInterval(timerInterval);
        timerInterval = null;
    }
}

// ========================================
// GAME LOGIC
// ========================================

function startGame() {
    stopTimer();

    gameStarted = true;
    gameOver = false;
    score = 0;

    guessedStates.clear();

    document.getElementById('score').textContent = '0/50';
    document.getElementById('timer').textContent = '0:00';

    inputContainer.style.display = 'block';

    stateInput.value = '';
    stateInput.focus();

    startBtn.style.display = 'none';
    giveUpBtn.style.display = 'inline-block';

    startTimer();
    drawMap();
}

function endGame() {
    if (gameOver) {
        return;
    }

    gameOver = true;
    gameStarted = false;

    stopTimer();

    inputContainer.style.display = 'none';

    startBtn.style.display = 'inline-block';
    startBtn.textContent = 'Play Again';

    giveUpBtn.style.display = 'none';

    // Update high score.
    if (score > highScore) {
        highScore = score;

        document.getElementById('highScore').textContent =
            `${highScore}/50`;
    }

    // Save progress.
    updateProgress(score, score === 50);

    // Find missed states.
    const missedStates = statesData
        .filter(s => !guessedStates.has(s.name))
        .map(s => s.name);

    console.log('Missed states:', missedStates);

    drawMap();
}

// ========================================
// CHECK ANSWER
// ========================================

function checkGuess(guess) {
    if (!guess || guess.trim() === '') {
        return;
    }

    // Normalize input.
    const normalized = guess.trim()
        .split(' ')
        .map(word =>
            word.charAt(0).toUpperCase() +
            word.slice(1).toLowerCase()
        )
        .join(' ');

    console.log('Checking guess:', normalized);

    const state = statesData.find(
        s => s.name === normalized
    );

    // CORRECT ANSWER
    if (state && !guessedStates.has(state.name)) {
        console.log('Correct state found:', state.name);

        playSound('correct');

        guessedStates.add(state.name);
        score++;

        document.getElementById('score').textContent =
            `${score}/50`;

        stateInput.value = '';

        // Flash green.
        stateInput.style.backgroundColor = '#c8e6c9';
        stateInput.style.borderColor = '#4CAF50';

        // Success message.
        const statusMsg = document.getElementById('statusMessage');

        if (statusMsg) {
            statusMsg.textContent = `✓ ${state.name} is correct!`;
            statusMsg.style.color = '#4CAF50';
        }

        setTimeout(() => {
            stateInput.style.backgroundColor = 'white';
            stateInput.style.borderColor = '#667eea';

            if (statusMsg) {
                statusMsg.textContent = 'Keep going...';
                statusMsg.style.color = 'white';
            }
        }, 800);

        drawMap();

        if (score === 50) {
            setTimeout(endGame, 1000);
        }

    // ALREADY GUESSED
    } else if (guessedStates.has(normalized)) {
        playSound('wrong');

        stateInput.value = '';

        stateInput.style.backgroundColor = '#fff9c4';
        stateInput.style.borderColor = '#FFC107';

        const statusMsg = document.getElementById('statusMessage');

        if (statusMsg) {
            statusMsg.textContent = `Already guessed ${normalized}`;
            statusMsg.style.color = '#FFC107';
        }

        setTimeout(() => {
            stateInput.style.backgroundColor = 'white';
            stateInput.style.borderColor = '#667eea';

            if (statusMsg) {
                statusMsg.textContent = 'Try another state...';
                statusMsg.style.color = 'white';
            }
        }, 800);

    // WRONG ANSWER
    } else {
        console.log('State not found:', normalized);

        playSound('wrong');

        stateInput.style.backgroundColor = '#ffcdd2';
        stateInput.style.borderColor = '#f44336';

        const statusMsg = document.getElementById('statusMessage');

        if (statusMsg) {
            statusMsg.textContent =
                `"${normalized}" is not correct`;

            statusMsg.style.color = '#f44336';
        }

        setTimeout(() => {
            stateInput.style.backgroundColor = 'white';
            stateInput.style.borderColor = '#667eea';

            if (statusMsg) {
                statusMsg.textContent = 'Try again...';
                statusMsg.style.color = 'white';
            }
        }, 800);
    }
}

// ========================================
// EVENT LISTENERS
// ========================================

startBtn.addEventListener('click', startGame);

giveUpBtn.addEventListener('click', () => {
    if (
        confirm(
            'Are you sure you want to give up and see all states?'
        )
    ) {
        // Reveal all remaining states.
        statesData.forEach(state => {
            if (!guessedStates.has(state.name)) {
                guessedStates.add(state.name);
            }
        });

        drawMap();
        endGame();
    }
});

// Handle Enter key.
stateInput.addEventListener('keydown', (e) => {
    if (e.key === 'Enter') {
        e.preventDefault();

        if (gameStarted && !gameOver) {
            const guess = stateInput.value;

            console.log('Enter pressed, checking guess:', guess);

            checkGuess(guess);
        }
    }
});

// Handle input change.
stateInput.addEventListener('change', () => {
    if (gameStarted && !gameOver) {
        checkGuess(stateInput.value);
    }
});

// ========================================
// INITIALIZE GAME
// ========================================

async function init() {
    await loadStatesData();
    await loadHighScore();

    drawMap();

    console.log(
        'Game initialized with',
        statesData.length,
        'states'
    );
}

init();
