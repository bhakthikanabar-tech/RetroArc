// Snake Game Implementation
const canvas = document.getElementById('gameCanvas');
const ctx = canvas.getContext('2d');

// Game settings
const gridSize = 20;
const tileCount = canvas.width / gridSize;

// Game state
let gameStarted = false;
let gameOver = false;
let score = 0;
let highScore = 0;

// Snake
let snake = [
    { x: 10, y: 10 }
];
let dx = 0;
let dy = 0;
let nextDirection = { dx: 0, dy: 0 };

// Food
let food = {
    x: 15,
    y: 15
};

// Game speed
let gameSpeed = 100;
let lastRenderTime = 0;

// Load high score
async function loadHighScore() {
    try {
        const response = await fetch('/api/get_progress/snake');
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
async function updateProgress(finalScore, won) {
    try {
        await fetch('/api/update_progress', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                game_name: 'snake',
                score: finalScore,
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

function drawText(text, x, y, color, size = 30) {
    ctx.fillStyle = color;
    ctx.font = `${size}px Arial`;
    ctx.textAlign = 'center';
    ctx.fillText(text, x, y);
}

// Game logic
function resetGame() {
    snake = [{ x: 10, y: 10 }];
    dx = 0;
    dy = 0;
    nextDirection = { dx: 0, dy: 0 };
    score = 0;
    gameSpeed = 100;
    document.getElementById('score').textContent = score;
    placeFood();
    gameOver = false;
}

function placeFood() {
    food.x = Math.floor(Math.random() * tileCount);
    food.y = Math.floor(Math.random() * tileCount);
    
    // Make sure food doesn't spawn on snake
    for (let segment of snake) {
        if (segment.x === food.x && segment.y === food.y) {
            placeFood();
            return;
        }
    }
}

function updateSnake() {
    // Update direction
    dx = nextDirection.dx;
    dy = nextDirection.dy;
    
    if (dx === 0 && dy === 0) return;
    
    // Move snake
    const head = { x: snake[0].x + dx, y: snake[0].y + dy };
    
    // Check wall collision
    if (head.x < 0 || head.x >= tileCount || head.y < 0 || head.y >= tileCount) {
        endGame();
        return;
    }
    
    // Check self collision
    for (let segment of snake) {
        if (segment.x === head.x && segment.y === head.y) {
            endGame();
            return;
        }
    }
    
    snake.unshift(head);
    
    // Check food collision
    if (head.x === food.x && head.y === food.y) {
        score++;
        document.getElementById('score').textContent = score;
        placeFood();
        
        // Increase speed slightly
        gameSpeed = Math.max(50, gameSpeed - 2);
    } else {
        snake.pop();
    }
}

function endGame() {
    gameOver = true;
    gameStarted = false;
    
    // Update high score
    if (score > highScore) {
        highScore = score;
        document.getElementById('highScore').textContent = highScore;
    }
    
    // Save progress (won if score > 20)
    updateProgress(score, score > 20);
}

function draw() {
    // Clear canvas
    drawRect(0, 0, canvas.width, canvas.height, '#000');
    
    // Draw grid (optional)
    ctx.strokeStyle = 'rgba(255, 255, 255, 0.1)';
    ctx.lineWidth = 1;
    for (let i = 0; i < tileCount; i++) {
        ctx.beginPath();
        ctx.moveTo(i * gridSize, 0);
        ctx.lineTo(i * gridSize, canvas.height);
        ctx.stroke();
        
        ctx.beginPath();
        ctx.moveTo(0, i * gridSize);
        ctx.lineTo(canvas.width, i * gridSize);
        ctx.stroke();
    }
    
    // Draw snake
    snake.forEach((segment, index) => {
        if (index === 0) {
            // Head
            drawRect(
                segment.x * gridSize + 1,
                segment.y * gridSize + 1,
                gridSize - 2,
                gridSize - 2,
                '#0f0'
            );
        } else {
            // Body
            drawRect(
                segment.x * gridSize + 1,
                segment.y * gridSize + 1,
                gridSize - 2,
                gridSize - 2,
                '#fff'
            );
        }
    });
    
    // Draw food
    drawCircle(
        food.x * gridSize + gridSize / 2,
        food.y * gridSize + gridSize / 2,
        gridSize / 2 - 2,
        '#ff1493'
    );
    
    // Draw start message
    if (!gameStarted && !gameOver) {
        drawText('Press SPACE to Start', canvas.width / 2, canvas.height / 2, 'white', 30);
        drawText('Use Arrow Keys to Move', canvas.width / 2, canvas.height / 2 + 40, 'white', 20);
    }
    
    // Draw game over message
    if (gameOver) {
        drawText('GAME OVER!', canvas.width / 2, canvas.height / 2 - 30, 'white', 40);
        drawText(`Score: ${score}`, canvas.width / 2, canvas.height / 2 + 20, 'white', 30);
        drawText('Press SPACE to Restart', canvas.width / 2, canvas.height / 2 + 60, 'white', 20);
    }
}

function gameLoop(currentTime) {
    requestAnimationFrame(gameLoop);
    
    const timeSinceLastRender = currentTime - lastRenderTime;
    
    if (timeSinceLastRender < gameSpeed) {
        return;
    }
    
    lastRenderTime = currentTime;
    
    if (gameStarted && !gameOver) {
        updateSnake();
    }
    
    draw();
}

// Event listeners
document.addEventListener('keydown', (e) => {
    // Prevent arrow keys from scrolling
    if (['ArrowUp', 'ArrowDown', 'ArrowLeft', 'ArrowRight', ' '].includes(e.key)) {
        e.preventDefault();
    }
    
    // Direction controls
    if (e.key === 'ArrowUp' && dy === 0) {
        nextDirection = { dx: 0, dy: -1 };
    } else if (e.key === 'ArrowDown' && dy === 0) {
        nextDirection = { dx: 0, dy: 1 };
    } else if (e.key === 'ArrowLeft' && dx === 0) {
        nextDirection = { dx: -1, dy: 0 };
    } else if (e.key === 'ArrowRight' && dx === 0) {
        nextDirection = { dx: 1, dy: 0 };
    }
    
    // Start/restart game
    if (e.key === ' ') {
        if (!gameStarted) {
            resetGame();
            gameStarted = true;
        }
    }
});

// Initialize
loadHighScore();
placeFood();
requestAnimationFrame(gameLoop);
