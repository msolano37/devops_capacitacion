const canvas = document.getElementById("game");
const ctx = canvas.getContext("2d");
const overlay = document.getElementById("overlay");
const scoreEl = document.getElementById("score");
const bestEl = document.getElementById("best");
const restartBtn = document.getElementById("restart");

const state = {
  running: false,
  score: 0,
  best: 0,
  gravity: 0.42,
  flapStrength: -7.5,
  speed: 2.2,
  bird: {
    x: 120,
    y: 280,
    radius: 22,
    velocity: 0,
    rotation: 0,
  },
  towers: [],
  frame: 0,
};

const towerConfig = {
  width: 70,
  gap: 170,
  spacing: 220,
  minHeight: 120,
};

const cloudColors = ["rgba(255,255,255,0.9)", "rgba(255,255,255,0.6)"];
const clouds = Array.from({ length: 6 }, (_, i) => ({
  x: 80 + i * 120,
  y: 40 + (i % 3) * 35,
  speed: 0.4 + (i % 2) * 0.2,
}));

function resetGame() {
  state.running = false;
  state.score = 0;
  state.bird.y = 280;
  state.bird.velocity = 0;
  state.bird.rotation = 0;
  state.towers = [];
  state.frame = 0;
  scoreEl.textContent = "0";
  overlay.classList.remove("hidden");
}

function startGame() {
  if (state.running) return;
  state.running = true;
  overlay.classList.add("hidden");
}

function flap() {
  if (!state.running) {
    startGame();
  }
  state.bird.velocity = state.flapStrength;
}

function spawnTower() {
  const maxHeight = canvas.height - towerConfig.gap - towerConfig.minHeight;
  const topHeight = Math.floor(
    towerConfig.minHeight + Math.random() * (maxHeight - towerConfig.minHeight)
  );
  state.towers.push({
    x: canvas.width + towerConfig.width,
    topHeight,
    passed: false,
  });
}

function updateBird() {
  state.bird.velocity += state.gravity;
  state.bird.y += state.bird.velocity;
  state.bird.rotation = Math.min(Math.max(state.bird.velocity / 10, -0.5), 0.7);
}

function updateTowers() {
  state.towers.forEach((tower) => {
    tower.x -= state.speed;
    if (!tower.passed && tower.x + towerConfig.width < state.bird.x) {
      tower.passed = true;
      state.score += 1;
      scoreEl.textContent = state.score;
      if (state.score > state.best) {
        state.best = state.score;
        bestEl.textContent = state.best;
      }
    }
  });
  if (state.towers.length && state.towers[0].x + towerConfig.width < -30) {
    state.towers.shift();
  }
  if (state.frame % 130 === 0) {
    spawnTower();
  }
}

function updateClouds() {
  clouds.forEach((cloud) => {
    cloud.x -= cloud.speed;
    if (cloud.x < -60) {
      cloud.x = canvas.width + 50;
    }
  });
}

function checkCollision() {
  if (state.bird.y - state.bird.radius < 0 || state.bird.y + state.bird.radius > canvas.height) {
    return true;
  }
  return state.towers.some((tower) => {
    const withinX =
      state.bird.x + state.bird.radius > tower.x &&
      state.bird.x - state.bird.radius < tower.x + towerConfig.width;
    if (!withinX) return false;
    const topCollision = state.bird.y - state.bird.radius < tower.topHeight;
    const bottomCollision =
      state.bird.y + state.bird.radius > tower.topHeight + towerConfig.gap;
    return topCollision || bottomCollision;
  });
}

function drawClouds() {
  clouds.forEach((cloud, index) => {
    ctx.fillStyle = cloudColors[index % cloudColors.length];
    ctx.beginPath();
    ctx.ellipse(cloud.x, cloud.y, 28, 14, 0, 0, Math.PI * 2);
    ctx.ellipse(cloud.x + 20, cloud.y + 6, 20, 12, 0, 0, Math.PI * 2);
    ctx.fill();
  });
}

function drawBird() {
  ctx.save();
  ctx.translate(state.bird.x, state.bird.y);
  ctx.rotate(state.bird.rotation);
  ctx.fillStyle = "#f4a261";
  ctx.beginPath();
  ctx.arc(0, 0, state.bird.radius, 0, Math.PI * 2);
  ctx.fill();

  ctx.fillStyle = "#1d1d1d";
  ctx.fillRect(-12, -12, 24, 8);
  ctx.fillStyle = "#ffffff";
  ctx.fillRect(-8, -10, 8, 4);

  ctx.fillStyle = "#ffb703";
  ctx.beginPath();
  ctx.moveTo(state.bird.radius - 2, 0);
  ctx.lineTo(state.bird.radius + 14, 6);
  ctx.lineTo(state.bird.radius + 14, -6);
  ctx.closePath();
  ctx.fill();

  ctx.fillStyle = "#8d5524";
  ctx.fillText("CAGE", -16, 28);
  ctx.restore();
}

function drawTowers() {
  ctx.fillStyle = "#2a9d8f";
  ctx.strokeStyle = "#0f3d3e";
  ctx.lineWidth = 4;

  state.towers.forEach((tower) => {
    ctx.fillRect(tower.x, 0, towerConfig.width, tower.topHeight);
    ctx.strokeRect(tower.x, 0, towerConfig.width, tower.topHeight);

    const bottomY = tower.topHeight + towerConfig.gap;
    ctx.fillRect(tower.x, bottomY, towerConfig.width, canvas.height - bottomY);
    ctx.strokeRect(tower.x, bottomY, towerConfig.width, canvas.height - bottomY);
  });
}

function drawGround() {
  const gradient = ctx.createLinearGradient(0, canvas.height - 80, 0, canvas.height);
  gradient.addColorStop(0, "#2b2d42");
  gradient.addColorStop(1, "#0b0d17");
  ctx.fillStyle = gradient;
  ctx.fillRect(0, canvas.height - 80, canvas.width, 80);
}

function drawScore() {
  ctx.fillStyle = "rgba(255,255,255,0.85)";
  ctx.font = "24px 'Segoe UI', sans-serif";
  ctx.fillText(`Puntuación: ${state.score}`, 20, 40);
}

function update() {
  ctx.clearRect(0, 0, canvas.width, canvas.height);
  drawClouds();
  drawTowers();
  drawGround();
  drawBird();
  drawScore();

  if (!state.running) {
    return;
  }

  updateBird();
  updateTowers();
  updateClouds();

  if (checkCollision()) {
    state.running = false;
    overlay.querySelector("h2").textContent = "¡Chocaste! Presiona para reiniciar";
    overlay.classList.remove("hidden");
  }

  state.frame += 1;
  window.requestAnimationFrame(update);
}

window.addEventListener("keydown", (event) => {
  if (event.code === "Space") {
    event.preventDefault();
    flap();
  }
});

canvas.addEventListener("pointerdown", () => flap());
restartBtn.addEventListener("click", () => {
  resetGame();
  startGame();
  state.frame = 0;
  window.requestAnimationFrame(update);
});

resetGame();
window.requestAnimationFrame(update);
