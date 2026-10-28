// ========================================
// RETROARC - SNAKE GAME
// ========================================

const canvas = document.getElementById('gameCanvas');
const ctx = canvas.getContext('2d');

// Game settings
const gridSize = 20;
const tileCount = canvas.width / gridSize;

// Speed settings
const initialSpeed = 180;
const minimumSpeed = 70;
const speedIncrease = 5;

let gameSpeed = initialSpeed;
let lastRenderTime = 0;

// Game state
let gameStarted = false;
let gameOver = false;
let score = 0;
let highScore = 0;

// Snake
let snake = [{ x: 10, y: 10 }];

let dx = 0;
let dy = 0;

let nextDirection = { dx: 0, dy: 0 };

// Food
let food = { x: 15, y: 15 };

// ========================================
// LOAD HIGH SCORE
// ========================================

async function loadHighScore() {
    try {
        const response = await fetch('/api/get_progress/snake');

        if (!response.ok) {
            throw new Error('Could not load high score');
        }

        const data = await response.json();

        highScore = Number(data.high_score) || 0;

        document.getElementById('highScore').textContent = highScore;

    } catch (error) {
        console.error('Error loading high score:', error);
    }
}

// ========================================
// SAVE GAME PROGRESS
// ========================================

async function updateProgress(finalScore, won) {
    try {
        const response = await fetch('/api/update_progress', {
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

        if (!response.ok) {
            throw new Error('Could not update game progress');
        }

    } catch (error) {
        console.error('Error updating progress:', error);
    }
}

// ========================================
// DRAWING HELPERS
// ========================================

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
    ctx.font = `bold ${size}px "Courier New", monospace`;
    ctx.textAlign = 'center';
    ctx.fillText(text, x, y);
}

// ========================================
// RESET GAME
// ========================================

function resetGame() {
    snake = [{ x: 10, y: 10 }];

    dx = 0;
    dy = 0;

    nextDirection = { dx: 0, dy: 0 };

    score = 0;

    // Start every new game at the slowest speed.
    gameSpeed = initialSpeed;

    lastRenderTime = 0;

    gameStarted = true;
    gameOver = false;

    document.getElementById('score').textContent = score;

    placeFood();
}

// ========================================
// PLACE FOOD
// ========================================

function placeFood() {
    // Find an empty tile for the food.
    const emptyTiles = [];

    for (let x = 0; x < tileCount; x++) {
        for (let y = 0; y < tileCount; y++) {
            const occupied = snake.some(segment =>
                segment.x === x && segment.y === y
            );

            if (!occupied) {
                emptyTiles.push({ x, y });
            }
        }
    }

    // The snake has filled the entire board.
    if (emptyTiles.length === 0) {
        endGame(true);
        return;
    }

    const randomIndex = Math.floor(
        Math.random() * emptyTiles.length
    );

    food = emptyTiles[randomIndex];
}

// ========================================
// UPDATE SNAKE
// ========================================

function updateSnake() {
    // Apply the latest valid direction.
    dx = nextDirection.dx;
    dy = nextDirection.dy;

    // Wait until the player chooses a direction.
    if (dx === 0 && dy === 0) {
        return;
    }

    const head = {
        x: snake[0].x + dx,
        y: snake[0].y + dy
    };

    // Check collision with the walls.
    if (
        head.x < 0 ||
        head.x >= tileCount ||
        head.y < 0 ||
        head.y >= tileCount
    ) {
        endGame();
        return;
    }

    // Check whether the snake is about to eat food.
    const eatingFood =
        head.x === food.x && head.y === food.y;

    // When not eating, the tail moves away this turn.
    // This means moving into the current tail position is safe.
    const bodyToCheck = eatingFood
        ? snake
        : snake.slice(0, -1);

    // Check collision with the snake's own body.
    const hitSelf = bodyToCheck.some(segment =>
        segment.x === head.x && segment.y === head.y
    );

    if (hitSelf) {
        endGame();
        return;
    }

    // Move the snake forward.
    snake.unshift(head);

    if (eatingFood) {
        // Increase score.
        score++;

        document.getElementById('score').textContent = score;

        // Increase speed gradually as food is collected.
        gameSpeed = Math.max(
            minimumSpeed,
            initialSpeed - score * speedIncrease
        );

        // Place new food.
        placeFood();

        // The board may be completely filled.
        if (gameOver) {
            return;
        }

    } else {
        // Remove the tail to maintain the same length.
        snake.pop();
    }
}

// ========================================
// END GAME
// ========================================

function endGame(won = false) {
    // Prevent duplicate progress submissions.
    if (gameOver) {
        return;
    }

    gameOver = true;
    gameStarted = false;

    // Update high score.
    if (score > highScore) {
        highScore = score;

        document.getElementById('highScore').textContent = highScore;
    }

    // Save the final score to the Flask backend.
    updateProgress(score, won || score > 20);

    draw();
}

// ========================================
// DRAW GAME BOARD
// ========================================

function drawBackground() {
    // Dark arcade background.
    drawRect(0, 0, canvas.width, canvas.height, '#05070b');

    // Subtle grid lines.
    ctx.strokeStyle = 'rgba(53, 242, 228, 0.09)';
    ctx.lineWidth = 1;

    for (let i = 0; i <= tileCount; i++) {
        // Vertical lines.
        ctx.beginPath();
        ctx.moveTo(i * gridSize, 0);
        ctx.lineTo(i * gridSize, canvas.height);
        ctx.stroke();

        // Horizontal lines.
        ctx.beginPath();
        ctx.moveTo(0, i * gridSize);
        ctx.lineTo(canvas.width, i * gridSize);
        ctx.stroke();
    }
}

// ========================================
// DRAW SNAKE
// ========================================

function drawSnake() {
    snake.forEach((segment, index) => {
        const x = segment.x * gridSize + 1;
        const y = segment.y * gridSize + 1;
        const size = gridSize - 2;

        if (index === 0) {
            // Snake head.
            drawRect(x, y, size, size, '#35f2e4');

            // Small eyes to make the head recognizable.
            ctx.fillStyle = '#05070b';

            if (dx !== 0 || dy !== 0) {
                const eyeSize = 3;

                if (dx === 1) {
                    ctx.fillRect(x + 12, y + 4, eyeSize, eyeSize);
                    ctx.fillRect(x + 12, y + 12, eyeSize, eyeSize);

                } else if (dx === -1) {
                    ctx.fillRect(x + 3, y + 4, eyeSize, eyeSize);
                    ctx.fillRect(x + 3, y + 12, eyeSize, eyeSize);

                } else if (dy === -1) {
                    ctx.fillRect(x + 4, y + 3, eyeSize, eyeSize);
                    ctx.fillRect(x + 12, y + 3, eyeSize, eyeSize);

                } else if (dy === 1) {
                    ctx.fillRect(x + 4, y + 12, eyeSize, eyeSize);
                    ctx.fillRect(x + 12, y + 12, eyeSize, eyeSize);
                }
            }

        } else {
            // Snake body.
            drawRect(x, y, size, size, '#24b8a9');
        }
    });
}

// ========================================
// DRAW FOOD
// ========================================

function drawFood() {
    const centerX = food.x * gridSize + gridSize / 2;
    const centerY = food.y * gridSize + gridSize / 2;

    // Pink food with a small glow.
    ctx.shadowColor = '#ff4fa3';
    ctx.shadowBlur = 10;

    drawCircle(
        centerX,
        centerY,
        gridSize / 2 - 3,
        '#ff4fa3'
    );

    ctx.shadowBlur = 0;
}

// ========================================
// DRAW MESSAGES
// ========================================

function drawOverlay() {
    if (gameStarted && !gameOver && (dx !== 0 || dy !== 0)) {
        return;
    }

    // Dark transparent overlay.
    ctx.fillStyle = 'rgba(5, 7, 11, 0.82)';
    ctx.fillRect(0, 0, canvas.width, canvas.height);

    if (gameOver) {
        drawText(
            'GAME OVER',
            canvas.width / 2,
            canvas.height / 2 - 35,
            '#ff4fa3',
            40
        );

        drawText(
            `SCORE: ${score}`,
            canvas.width / 2,
            canvas.height / 2 + 10,
            '#35f2e4',
            25
        );

        drawText(
            'PRESS SPACE TO PLAY AGAIN',
            canvas.width / 2,
            canvas.height / 2 + 55,
            '#ffd166',
            17
        );

    } else {
        drawText(
            'SNAKE',
            canvas.width / 2,
            canvas.height / 2 - 40,
            '#35f2e4',
            40
        );

        drawText(
            'PRESS SPACE TO START',
            canvas.width / 2,
            canvas.height / 2 + 10,
            '#ffd166',
            20
        );

        drawText(
            'USE ARROW KEYS TO MOVE',
            canvas.width / 2,
            canvas.height / 2 + 45,
            '#ffffff',
            16
        );
    }
}

// ========================================
// DRAW EVERYTHING
// ========================================

function draw() {
    drawBackground();
    drawFood();
    drawSnake();
    drawOverlay();
}

// ========================================
// GAME LOOP
// ========================================

function gameLoop(currentTime) {
    requestAnimationFrame(gameLoop);

    if (!gameStarted || gameOver) {
        draw();
        return;
    }

    const timeSinceLastRender = currentTime - lastRenderTime;

    // Wait until it is time for the next movement.
    if (timeSinceLastRender < gameSpeed) {
        return;
    }

    lastRenderTime = currentTime;

    updateSnake();
    draw();
}

// ========================================
// KEYBOARD CONTROLS
// ========================================

document.addEventListener('keydown', (event) => {
    const key = event.key;

    // Prevent arrow keys and Space from scrolling the page.
    if (
        ['ArrowUp', 'ArrowDown', 'ArrowLeft', 'ArrowRight', ' ']
            .includes(key)
    ) {
        event.preventDefault();
    }

    // Start or restart the game with Space.
    if (key === ' ') {
        if (!gameStarted) {
            resetGame();
            draw();
        }

        return;
    }

    // Ignore direction input when the game is over.
    if (gameOver || !gameStarted) {
        return;
    }

    // Use the current intended direction to prevent
    // reversing direction before the next movement.
    if (
        key === 'ArrowUp' &&
        nextDirection.dy !== 1 &&
        (dx !== 0 || dy !== 0 || nextDirection.dx !== 0)
    ) {
        nextDirection = { dx: 0, dy: -1 };

    } else if (
        key === 'ArrowDown' &&
        nextDirection.dy !== -1 &&
        (dx !== 0 || dy !== 0 || nextDirection.dx !== 0)
    ) {
        nextDirection = { dx: 0, dy: 1 };

    } else if (
        key === 'ArrowLeft' &&
        nextDirection.dx !== 1 &&
        (dx !== 0 || dy !== 0 || nextDirection.dy !== 0)
    ) {
        nextDirection = { dx: -1, dy: 0 };

    } else if (
        key === 'ArrowRight' &&
        nextDirection.dx !== -1 &&
        (dx !== 0 || dy !== 0 || nextDirection.dy !== 0)
    ) {
        nextDirection = { dx: 1, dy: 0 };
    }
});

// ========================================
// INITIALIZE GAME
// ========================================

document.getElementById('score').textContent = score;
document.getElementById('highScore').textContent = highScore;

loadHighScore();

placeFood();
draw();

requestAnimationFrame(gameLoop);
