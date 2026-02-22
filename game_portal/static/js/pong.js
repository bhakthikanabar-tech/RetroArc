// Pong Game Implementation
const canvas = document.getElementById('gameCanvas');
const ctx = canvas.getContext('2d');

// Game state
let gameStarted = false;
let gameOver = false;

// Paddle properties
const paddleWidth = 10;
const paddleHeight = 100;
const paddleSpeed = 8;

let leftPaddle = {
    x: 20,
    y: canvas.height / 2 - paddleHeight / 2,
    width: paddleWidth,
    height: paddleHeight,
    dy: 0
};

let rightPaddle = {
    x: canvas.width - 20 - paddleWidth,
    y: canvas.height / 2 - paddleHeight / 2,
    width: paddleWidth,
    height: paddleHeight,
    dy: 0
};

// Ball properties
let ball = {
    x: canvas.width / 2,
    y: canvas.height / 2,
    radius: 8,
    dx: 5,
    dy: 5,
    speed: 5
};

// Scores
let leftScore = 0;
let rightScore = 0;
let highScore = 0;

// Key states
const keys = {};

// Load high score
async function loadHighScore() {
    try {
        const response = await fetch('/api/get_progress/pong');
        const data = await response.json();
        if (data.high_score) {
            highScore = data.high_score;
            document.getElementById('highScore').textContent = highScore;
        }
    } catch (error) {
        console.error('Error loading high score:', error);
    }
}

// Update progress
async function updateProgress(score, won) {
    try {
        await fetch('/api/update_progress', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                game_name: 'pong',
                score: score,
                won: won
            })
        });
    } catch (error) {
        console.error('Error updating progress:', error);
    }
}

// Draw functions
function drawRect(x, y, width, height, color) {
    ctx.fillStyle = color;
    ctx.fillRect(x, y, width, height);
}

function drawCircle(x, y, radius, color) {
    ctx.fillStyle = color;
    ctx.beginPath();
    ctx.arc(x, y, radius, 0, Math.PI * 2);
    ctx.fill();
}

function drawNet() {
    for (let i = 0; i < canvas.height; i += 20) {
        drawRect(canvas.width / 2 - 2, i, 4, 10, 'rgba(255, 255, 255, 0.3)');
    }
}

function drawText(text, x, y, color, size = 30) {
    ctx.fillStyle = color;
    ctx.font = `${size}px Arial`;
    ctx.textAlign = 'center';
    ctx.fillText(text, x, y);
}

// Game logic
function resetBall() {
    ball.x = canvas.width / 2;
    ball.y = canvas.height / 2;
    ball.dx = (Math.random() > 0.5 ? 1 : -1) * 5;
    ball.dy = (Math.random() - 0.5) * 10;
    ball.speed = 5;
}

function updatePaddles() {
    // Left paddle
    if (keys['w'] && leftPaddle.y > 0) {
        leftPaddle.y -= paddleSpeed;
    }
    if (keys['s'] && leftPaddle.y < canvas.height - leftPaddle.height) {
        leftPaddle.y += paddleSpeed;
    }
    
    // Right paddle
    if (keys['ArrowUp'] && rightPaddle.y > 0) {
        rightPaddle.y -= paddleSpeed;
    }
    if (keys['ArrowDown'] && rightPaddle.y < canvas.height - rightPaddle.height) {
        rightPaddle.y += paddleSpeed;
    }
}

function updateBall() {
    ball.x += ball.dx;
    ball.y += ball.dy;
    
    // Top and bottom collision
    if (ball.y + ball.radius > canvas.height || ball.y - ball.radius < 0) {
        ball.dy *= -1;
    }
    
    // Left paddle collision
    if (ball.x - ball.radius < leftPaddle.x + leftPaddle.width &&
        ball.y > leftPaddle.y &&
        ball.y < leftPaddle.y + leftPaddle.height) {
        ball.dx = Math.abs(ball.dx) * 1.05;
        ball.dy += (ball.y - (leftPaddle.y + leftPaddle.height / 2)) * 0.1;
    }
    
    // Right paddle collision
    if (ball.x + ball.radius > rightPaddle.x &&
        ball.y > rightPaddle.y &&
        ball.y < rightPaddle.y + rightPaddle.height) {
        ball.dx = -Math.abs(ball.dx) * 1.05;
        ball.dy += (ball.y - (rightPaddle.y + rightPaddle.height / 2)) * 0.1;
    }
    
    // Score points
    if (ball.x - ball.radius < 0) {
        rightScore++;
        document.getElementById('rightScore').textContent = rightScore;
        resetBall();
        checkGameOver();
    }
    
    if (ball.x + ball.radius > canvas.width) {
        leftScore++;
        document.getElementById('leftScore').textContent = leftScore;
        resetBall();
        checkGameOver();
    }
}

function checkGameOver() {
    if (leftScore >= 6 || rightScore >= 6) {
        gameOver = true;
        gameStarted = false;
        const totalScore = leftScore + rightScore;
        const won = (leftScore >= 6);
        updateProgress(totalScore, won);
        
        if (totalScore > highScore) {
            highScore = totalScore;
            document.getElementById('highScore').textContent = highScore;
        }
    }
}

function draw() {
    // Clear canvas
    drawRect(0, 0, canvas.width, canvas.height, '#000');
    
    // Draw net
    drawNet();
    
    // Draw paddles
    drawRect(leftPaddle.x, leftPaddle.y, leftPaddle.width, leftPaddle.height, '#fff');
    drawRect(rightPaddle.x, rightPaddle.y, rightPaddle.width, rightPaddle.height, '#fff');
    
    // Draw ball
    drawCircle(ball.x, ball.y, ball.radius, '#fff');
    
    // Draw start message
    if (!gameStarted && !gameOver) {
        drawText('Press SPACE to Start', canvas.width / 2, canvas.height / 2, 'white', 30);
    }
    
    // Draw game over message
    if (gameOver) {
        drawText('GAME OVER!', canvas.width / 2, canvas.height / 2 - 30, 'white', 40);
        const winner = leftScore >= 6 ? 'Left Player' : 'Right Player';
        drawText(`${winner} Wins!`, canvas.width / 2, canvas.height / 2 + 20, 'white', 30);
        drawText('Press SPACE to Restart', canvas.width / 2, canvas.height / 2 + 60, 'white', 20);
    }
}

function gameLoop() {
    if (gameStarted && !gameOver) {
        updatePaddles();
        updateBall();
    }
    draw();
    requestAnimationFrame(gameLoop);
}

// Event listeners
document.addEventListener('keydown', (e) => {
    keys[e.key] = true;
    
    if (e.key === ' ') {
        e.preventDefault();
        if (!gameStarted) {
            if (gameOver) {
                // Reset game
                leftScore = 0;
                rightScore = 0;
                document.getElementById('leftScore').textContent = leftScore;
                document.getElementById('rightScore').textContent = rightScore;
                gameOver = false;
            }
            gameStarted = true;
            resetBall();
        }
    }
});

document.addEventListener('keyup', (e) => {
    keys[e.key] = false;
});

// Initialize
loadHighScore();
gameLoop();
