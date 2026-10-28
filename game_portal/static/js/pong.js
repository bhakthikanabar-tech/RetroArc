// ============================================
// RETROARC - PONG GAME
// Supports Single Player (AI) and Two Players
// ============================================

const canvas = document.getElementById("gameCanvas");
const ctx = canvas.getContext("2d");

// UI Elements
const singlePlayerBtn = document.getElementById("singlePlayerBtn");
const twoPlayerBtn = document.getElementById("twoPlayerBtn");

const leftScoreElement = document.getElementById("leftScore");
const rightScoreElement = document.getElementById("rightScore");
const highScoreElement = document.getElementById("highScore");

const leftPlayerLabel = document.getElementById("leftPlayerLabel");
const rightPlayerLabel = document.getElementById("rightPlayerLabel");

const modeDescription = document.getElementById("modeDescription");
const rightPlayerControls = document.getElementById("rightPlayerControls");
const gameStatus = document.getElementById("gameStatus");

const startBtn = document.getElementById("startBtn");
const restartBtn = document.getElementById("restartBtn");

// ============================================
// GAME CONFIGURATION
// ============================================

const WIDTH = canvas.width;
const HEIGHT = canvas.height;

const PADDLE_WIDTH = 14;
const PADDLE_HEIGHT = 100;

const BALL_RADIUS = 9;

const WINNING_SCORE = 5;

// Game mode: "single" or "two"
let gameMode = "single";

// Game states:
// ready, playing, paused, gameover
let gameState = "ready";

// Keyboard controls
const keys = {};

// Scores
let leftScore = 0;
let rightScore = 0;

// High score is saved in the browser
const HIGH_SCORE_KEY = "retroarc_pong_highscore";

let highScore = 0;

try {
    highScore = Number(
        localStorage.getItem(HIGH_SCORE_KEY)
    ) || 0;
} catch (error) {
    console.warn("Unable to load high score.", error);
}

// ============================================
// PADDLES
// ============================================

const leftPaddle = {
    x: 25,
    y: HEIGHT / 2 - PADDLE_HEIGHT / 2,
    width: PADDLE_WIDTH,
    height: PADDLE_HEIGHT,
    speed: 7,
    color: "#f5c451"
};

const rightPaddle = {
    x: WIDTH - 25 - PADDLE_WIDTH,
    y: HEIGHT / 2 - PADDLE_HEIGHT / 2,
    width: PADDLE_WIDTH,
    height: PADDLE_HEIGHT,
    speed: 7,
    color: "#ff784f"
};

// ============================================
// BALL
// ============================================

const ball = {
    x: WIDTH / 2,
    y: HEIGHT / 2,
    radius: BALL_RADIUS,
    speed: 5,
    velocityX: 0,
    velocityY: 0,
    maxSpeed: 12
};

// ============================================
// GAME MODE SELECTION
// ============================================

singlePlayerBtn.addEventListener("click", () => {
    selectMode("single");
});

twoPlayerBtn.addEventListener("click", () => {
    selectMode("two");
});

function selectMode(mode) {
    if (mode !== "single" && mode !== "two") {
        return;
    }

    gameMode = mode;

    // Stop the current match and reset scores.
    resetGame(false);

    // Update selected button.
    singlePlayerBtn.classList.toggle(
        "active",
        mode === "single"
    );

    twoPlayerBtn.classList.toggle(
        "active",
        mode === "two"
    );

    // Update player names and instructions.
    if (mode === "single") {
        leftPlayerLabel.textContent = "Player 1";
        rightPlayerLabel.textContent = "Computer";

        modeDescription.textContent =
            "Play against the computer! Can you beat the AI?";

        rightPlayerControls.innerHTML =
            "<strong>Computer:</strong> Controlled by AI";
    } else {
        leftPlayerLabel.textContent = "Player 1";
        rightPlayerLabel.textContent = "Player 2";

        modeDescription.textContent =
            "Challenge a friend in local multiplayer!";

        rightPlayerControls.innerHTML =
            "<strong>Player 2:</strong> Arrow Up / Arrow Down";
    }

    gameStatus.textContent =
        "Mode selected! Press Start Game to play.";

    startBtn.textContent = "▶ Start Game";

    drawGame();
}

// ============================================
// KEYBOARD CONTROLS
// ============================================

document.addEventListener("keydown", (event) => {
    const key = event.key.toLowerCase();

    // Prevent arrow keys and space from scrolling the page.
    if (
        ["arrowup", "arrowdown", " "].includes(key)
    ) {
        event.preventDefault();
    }

    keys[key] = true;

    // Start, pause, or resume with Space.
    if (event.code === "Space" && !event.repeat) {
        toggleGame();
    }
});

document.addEventListener("keyup", (event) => {
    keys[event.key.toLowerCase()] = false;
});

// Prevent stuck keys when the browser loses focus.
window.addEventListener("blur", () => {
    Object.keys(keys).forEach((key) => {
        keys[key] = false;
    });
});

// ============================================
// START / PAUSE / RESUME
// ============================================

startBtn.addEventListener("click", toggleGame);

function toggleGame() {
    if (gameState === "playing") {
        gameState = "paused";

        gameStatus.textContent = "Game paused.";

        startBtn.textContent = "▶ Resume Game";

        drawGame();

        return;
    }

    if (gameState === "gameover") {
        return;
    }

    if (gameState === "ready") {
        serveBall();
    }

    gameState = "playing";

    gameStatus.textContent = "Game in progress!";

    startBtn.textContent = "⏸ Pause Game";
}

// ============================================
// RESTART GAME
// ============================================

restartBtn.addEventListener("click", () => {
    resetGame(true);
});

function resetGame(startImmediately = false) {
    leftScore = 0;
    rightScore = 0;

    leftPaddle.y = HEIGHT / 2 - PADDLE_HEIGHT / 2;
    rightPaddle.y = HEIGHT / 2 - PADDLE_HEIGHT / 2;

    resetBall();

    gameState = "ready";

    updateScoreboard();

    if (startImmediately) {
        serveBall();

        gameState = "playing";

        gameStatus.textContent = "Game restarted!";

        startBtn.textContent = "⏸ Pause Game";
    } else {
        gameStatus.textContent =
            "Press Start Game when you're ready.";

        startBtn.textContent = "▶ Start Game";
    }

    drawGame();
}

// ============================================
// BALL MOVEMENT
// ============================================

function resetBall() {
    ball.x = WIDTH / 2;
    ball.y = HEIGHT / 2;

    ball.speed = 5;

    ball.velocityX = 0;
    ball.velocityY = 0;
}

function serveBall() {
    resetBall();

    // Serve toward a randomly selected player.
    const direction = Math.random() < 0.5 ? -1 : 1;

    ball.velocityX = direction * ball.speed;

    // Randomize the initial vertical movement.
    ball.velocityY = (Math.random() * 2 - 1) * 3;
}

// ============================================
// PLAYER MOVEMENT
// ============================================

function updatePlayerPaddles() {
    // Player 1: W and S.
    if (keys["w"]) {
        leftPaddle.y -= leftPaddle.speed;
    }

    if (keys["s"]) {
        leftPaddle.y += leftPaddle.speed;
    }

    // Player 2 controls the right paddle only
    // in two-player mode.
    if (gameMode === "two") {
        if (keys["arrowup"]) {
            rightPaddle.y -= rightPaddle.speed;
        }

        if (keys["arrowdown"]) {
            rightPaddle.y += rightPaddle.speed;
        }
    }

    // Keep paddles inside the canvas.
    leftPaddle.y = Math.max(
        0,
        Math.min(
            HEIGHT - leftPaddle.height,
            leftPaddle.y
        )
    );

    rightPaddle.y = Math.max(
        0,
        Math.min(
            HEIGHT - rightPaddle.height,
            rightPaddle.y
        )
    );
}

// ============================================
// COMPUTER AI
// ============================================

function updateAI() {
    if (gameMode !== "single") {
        return;
    }

    // The AI moves the right paddle toward the ball.
    const paddleCenter =
        rightPaddle.y + rightPaddle.height / 2;

    const difference = ball.y - paddleCenter;

    // Make the AI slightly less than perfect.
    const aiSpeed = 4.5;

    if (difference > 12) {
        rightPaddle.y += Math.min(aiSpeed, difference);
    } else if (difference < -12) {
        rightPaddle.y -= Math.min(aiSpeed, -difference);
    }

    // Keep the paddle inside the canvas.
    rightPaddle.y = Math.max(
        0,
        Math.min(
            HEIGHT - rightPaddle.height,
            rightPaddle.y
        )
    );
}

// ============================================
// BALL COLLISION
// ============================================

function updateBall() {
    ball.x += ball.velocityX;
    ball.y += ball.velocityY;

    // Bounce off top and bottom walls.
    if (
        ball.y - ball.radius <= 0 ||
        ball.y + ball.radius >= HEIGHT
    ) {
        ball.velocityY *= -1;

        // Keep the ball inside the canvas.
        ball.y = Math.max(
            ball.radius,
            Math.min(HEIGHT - ball.radius, ball.y)
        );
    }

    // Collision with left paddle.
    if (
        ball.velocityX < 0 &&
        ball.x - ball.radius <=
            leftPaddle.x + leftPaddle.width &&
        ball.x + ball.radius >= leftPaddle.x &&
        ball.y + ball.radius >= leftPaddle.y &&
        ball.y - ball.radius <=
            leftPaddle.y + leftPaddle.height
    ) {
        bounceOffPaddle(leftPaddle, 1);
    }

    // Collision with right paddle.
    if (
        ball.velocityX > 0 &&
        ball.x + ball.radius >= rightPaddle.x &&
        ball.x - ball.radius <=
            rightPaddle.x + rightPaddle.width &&
        ball.y + ball.radius >= rightPaddle.y &&
        ball.y - ball.radius <=
            rightPaddle.y + rightPaddle.height
    ) {
        bounceOffPaddle(rightPaddle, -1);
    }

    // Ball goes beyond the left boundary:
    // Player 2 or the computer scores.
    if (ball.x + ball.radius < 0) {
        rightScore++;

        handlePoint("right");
    }

    // Ball goes beyond the right boundary:
    // Player 1 scores.
    if (ball.x - ball.radius > WIDTH) {
        leftScore++;

        handlePoint("left");
    }
}

// ============================================
// PADDLE BOUNCE
// ============================================

function bounceOffPaddle(paddle, direction) {
    // Determine where the ball hits the paddle.
    const paddleCenter =
        paddle.y + paddle.height / 2;

    const hitPosition =
        (ball.y - paddleCenter) /
        (paddle.height / 2);

    // Change vertical direction according to
    // the point where the ball hits the paddle.
    const maxBounceAngle = Math.PI / 3;

    const bounceAngle =
        hitPosition * maxBounceAngle;

    // Increase the ball speed slightly.
    ball.speed = Math.min(
        ball.speed + 0.25,
        ball.maxSpeed
    );

    ball.velocityX =
        direction * ball.speed * Math.cos(bounceAngle);

    ball.velocityY =
        ball.speed * Math.sin(bounceAngle);

    // Move the ball outside the paddle to avoid
    // repeated collision detection.
    if (direction === 1) {
        ball.x = paddle.x + paddle.width + ball.radius;
    } else {
        ball.x = paddle.x - ball.radius;
    }
}

// ============================================
// SCORING AND WINNING
// ============================================

function handlePoint(scoringSide) {
    // Update the browser's saved high score.
    highScore = Math.max(
        highScore,
        leftScore,
        rightScore
    );

    try {
        localStorage.setItem(
            HIGH_SCORE_KEY,
            String(highScore)
        );
    } catch (error) {
        console.warn("Unable to save high score.", error);
    }

    updateScoreboard();

    // Check whether a player has won.
    if (
        leftScore >= WINNING_SCORE ||
        rightScore >= WINNING_SCORE
    ) {
        gameState = "gameover";

        const winner =
            leftScore >= WINNING_SCORE
                ? leftPlayerLabel.textContent
                : rightPlayerLabel.textContent;

        gameStatus.textContent =
            `🏆 ${winner} wins! Final score: ${leftScore} - ${rightScore}`;

        startBtn.textContent = "Game Over";

        drawGame();

        return;
    }

    // Reset the ball after a point.
    resetBall();

    // Brief pause before the next serve.
    gameState = "ready";

    const scorer =
        scoringSide === "left"
            ? leftPlayerLabel.textContent
            : rightPlayerLabel.textContent;

    gameStatus.textContent =
        `${scorer} scores! Press Space or Start Game to continue.`;

    startBtn.textContent = "▶ Continue Game";

    drawGame();
}

// ============================================
// UPDATE SCOREBOARD
// ============================================

function updateScoreboard() {
    leftScoreElement.textContent = leftScore;
    rightScoreElement.textContent = rightScore;
    highScoreElement.textContent = highScore;
}

// ============================================
// DRAWING FUNCTIONS
// ============================================

function drawBackground() {
    ctx.fillStyle = "#111111";

    ctx.fillRect(0, 0, WIDTH, HEIGHT);

    // Center dividing line.
    ctx.setLineDash([12, 12]);

    ctx.strokeStyle = "#555555";

    ctx.lineWidth = 3;

    ctx.beginPath();

    ctx.moveTo(WIDTH / 2, 0);
    ctx.lineTo(WIDTH / 2, HEIGHT);

    ctx.stroke();

    ctx.setLineDash([]);
}

function drawPaddle(paddle) {
    ctx.fillStyle = paddle.color;

    ctx.fillRect(
        paddle.x,
        paddle.y,
        paddle.width,
        paddle.height
    );
}

function drawBall() {
    ctx.beginPath();

    ctx.arc(
        ball.x,
        ball.y,
        ball.radius,
        0,
        Math.PI * 2
    );

    ctx.fillStyle = "#f5c451";

    ctx.shadowColor = "#f5c451";
    ctx.shadowBlur = 12;

    ctx.fill();

    ctx.shadowBlur = 0;
}

function drawGameMessage() {
    if (gameState === "playing") {
        return;
    }

    let message = "";

    if (gameState === "ready") {
        message = "PRESS SPACE TO PLAY";
    } else if (gameState === "paused") {
        message = "PAUSED";
    } else if (gameState === "gameover") {
        message = "GAME OVER";
    }

    ctx.fillStyle = "#ffffff";

    ctx.font = "bold 24px Arial";

    ctx.textAlign = "center";

    ctx.fillText(
        message,
        WIDTH / 2,
        HEIGHT / 2 - 35
    );
}

function drawGame() {
    drawBackground();

    drawPaddle(leftPaddle);

    drawPaddle(rightPaddle);

    drawBall();

    drawGameMessage();
}

// ============================================
// MAIN GAME LOOP
// ============================================

function gameLoop() {
    if (gameState === "playing") {
        updatePlayerPaddles();

        // Move the right paddle using AI
        // only when single-player mode is active.
        updateAI();

        updateBall();
    }

    drawGame();

    requestAnimationFrame(gameLoop);
}

// ============================================
// INITIALIZE GAME
// ============================================

updateScoreboard();

drawGame();

gameLoop();
