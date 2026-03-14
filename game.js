// ─────────────────────────────────────────────
// SPRITES
// ─────────────────────────────────────────────
const SPRITES_B64 = {
  agent:          'game_images/agent.png',
  saiyan:         'game_images/saiyan.png',
  enemy:          'game_images/enemy.png',
  zombie:         'game_images/zombie.png',
  bullet:         'game_images/bullet.png',
  gold_bullet:    'game_images/bullet_gold.png',
  heart:          'game_images/heart.png',
  shield:         'game_images/shield.png',
  lightning:      'game_images/lightning.png',
  cannon:         'game_images/cannon.png',
  bomb:           'game_images/bomb.png',
  bomb_exploding: 'game_images/bomb_exploding.png',
  poison:         'game_images/poison.png',
  barrier:        'game_images/barrier.png',
  star:           'game_images/star.png',
  honey:          'game_images/honey.png',
  firecracker_u:  'game_images/firecracker/firecracker_u.png',
  firecracker_l:  'game_images/firecracker/firecracker_l.png',
  firecracker_r:  'game_images/firecracker/firecracker_r.png',
  firecracker_d:  'game_images/firecracker/firecracker_d.png',
  firework:       'game_images/firework.png'
};

// ─────────────────────────────────────────────
// IMAGE LOADER
// ─────────────────────────────────────────────
const IMG = {};
let imagesLoaded = 0;
const imageKeys = Object.keys(SPRITES_B64);

function loadImages(cb) {
  imageKeys.forEach(key => {
    const img = new Image();
    img.src = SPRITES_B64[key];
    img.onload = () => { imagesLoaded++; if (imagesLoaded === imageKeys.length) cb(); };
    img.onerror = () => { imagesLoaded++; if (imagesLoaded === imageKeys.length) cb(); };
    IMG[key] = img;
  });
}

// Render powerup icons in the info section
function renderIconCanvases() {
  document.querySelectorAll('.pu-icon-canvas').forEach(c => {
    const key = c.dataset.key;
    if (!IMG[key]) return;
    const ctx = c.getContext('2d');
    ctx.imageSmoothingEnabled = false;
    ctx.drawImage(IMG[key], 0, 0, 32, 32);
  });
}

// ─────────────────────────────────────────────
// GAME
// ─────────────────────────────────────────────
const canvas = document.getElementById('gameCanvas');
const ctx = canvas.getContext('2d');
const overlay = document.getElementById('overlay');
const startBtn = document.getElementById('startBtn');
const overlaySubtitle = document.getElementById('overlaySubtitle');
const overlayControls = document.getElementById('overlayControls');

const W = 800, H = 800;
const SQUARE = 20;
const TAN = '#d2b48c';
const BROWN = '#3d2718';
const CHAR_SIZE = 50;
const ENEMY_SIZE = 50;
const BULLET_SIZE = 10;
const ITEM_SIZE = 40;
const CHAR_SPEED = 4;
const BULLET_SPEED = 10;
const ENEMY_SPEED = 6;
const ENEMY_SPEED_SLOW = 3;

let game = null, animId = null, keys = {};
let highScore = 0;

window.addEventListener('keydown', e => {
  keys[e.key] = true;
  if (['ArrowUp','ArrowDown','ArrowLeft','ArrowRight',' '].includes(e.key)) e.preventDefault();
  if (e.key === 'Enter') handleEnter();
});
window.addEventListener('keyup', e => { keys[e.key] = false; });

function handleEnter() {
  if (!game) return;
  if (game.state === 'menu') { startNewGame(); return; }
  if (game.state === 'gameover') { startNewGame(); return; }
}

startBtn.addEventListener('click', startNewGame);

function startNewGame() {
  overlay.classList.add('hidden');
  if (animId) cancelAnimationFrame(animId);
  game = createGame();
  loop();
}

// ─────────────────────────────────────────────
// GAME STATE
// ─────────────────────────────────────────────
function createGame() {
  // Hearts: 3, right-aligned
  const hearts = [];
  for (let i = 0; i < 3; i++) {
    hearts.push({ x: (W - 60) - i * 50, y: 20, size: ITEM_SIZE });
  }
  return {
    state: 'running',
    score: 0,
    tick: 0,
    // Spawn timing (ms equivalent via frame counting at 60fps)
    spawnDelay: 180,      // 3000ms / ~16.6ms per frame
    spawnTimer: 0,
    spawnSpeedupInterval: 1800, // 30000ms
    spawnSpeedupPct: 0.03,
    powerupTimer: 0,
    powerupSpawn: 600,    // 10000ms
    // Entities
    character: createCharacter(),
    bullets: [],
    enemies: [],
    hearts,
    shields: [],
    allies: [],
    // Powerup pickups on screen
    lightnings: [], cannons: [], bombs: [], infections: [],
    barriers: [], stars: [], honeys: [], firecrackers: [],
    fireworks: [],
    // Flags (matching game.py)
    bulletFired: false,
    infected: false,
    fourBullet: false,
    invulnerable: false,
    slowed: false,
    lights: false,         // firecracker mode
    lastEnemyLocation: [0, 0],
    hitCooldown: 0,
    bombActive: false,
    bombTimer: 0,
  };
}

function createCharacter() {
  return { x: W/2 - CHAR_SIZE/2, y: H/2 - CHAR_SIZE/2, speed: CHAR_SPEED, saiyan: false };
}

// ─────────────────────────────────────────────
// UPDATE
// ─────────────────────────────────────────────
function update() {
  if (game.state !== 'running') return;
  game.tick++;
  const g = game;
  const ch = g.character;

  // ── MOVE CHARACTER ──
  if ((keys['w'] || keys['W']) && ch.y > 0) ch.y -= ch.speed;
  if ((keys['s'] || keys['S']) && ch.y < H - CHAR_SIZE) ch.y += ch.speed;
  if ((keys['a'] || keys['A']) && ch.x > 0) ch.x -= ch.speed;
  if ((keys['d'] || keys['D']) && ch.x < W - CHAR_SIZE) ch.x += ch.speed;

  // ── SHOOTING ──
  const cx = ch.x + CHAR_SIZE/2, cy = ch.y + CHAR_SIZE/2;
  if (!g.fourBullet) {
    let dir = null;
    if (keys['ArrowUp'])    dir = 'up';
    if (keys['ArrowDown'])  dir = 'down';
    if (keys['ArrowLeft'])  dir = 'left';
    if (keys['ArrowRight']) dir = 'right';
    if (dir && !g.bulletFired) {
      g.bullets.push(makeBullet(cx, cy, dir, g));
      g.bulletFired = true;
    }
  } else {
    const anyArrow = keys['ArrowUp'] || keys['ArrowDown'] || keys['ArrowLeft'] || keys['ArrowRight'];
    if (anyArrow && !g.bulletFired) {
      ['up','down','left','right'].forEach(d => g.bullets.push(makeBullet(cx, cy, d, g)));
      g.bulletFired = true;
    }
  }
  if (!keys['ArrowUp'] && !keys['ArrowDown'] && !keys['ArrowLeft'] && !keys['ArrowRight']) {
    g.bulletFired = false;
  }

  // ── SPAWN ENEMIES ──
  g.spawnTimer++;
  if (g.spawnTimer >= g.spawnDelay) {
    g.spawnTimer = 0;
    g.enemies.push(makeEnemy(ch));
    // speedup every spawnSpeedupInterval frames
    if (g.tick % g.spawnSpeedupInterval === 0) {
      g.spawnDelay = Math.max(10, g.spawnDelay * (1 - g.spawnSpeedupPct));
    }
  }

  // ── SPAWN POWERUPS ──
  g.powerupTimer++;
  if (g.powerupTimer >= g.powerupSpawn) {
    g.powerupTimer = 0;
    spawnPowerup(g);
  }

  // ── MOVE BULLETS ──
  g.bullets = g.bullets.filter(b => {
    moveBullet(b);
    return b.x > -20 && b.x < W+20 && b.y > -20 && b.y < H+20;
  });

  // ── MOVE ENEMIES ──
  const enemySpeed = g.slowed ? ENEMY_SPEED_SLOW : ENEMY_SPEED;
  g.enemies.forEach(e => { e.speed = enemySpeed; });

  for (let i = g.enemies.length - 1; i >= 0; i--) {
    const e = g.enemies[i];
    // Find nearest target: character or nearest ally
    let tx = ch.x + CHAR_SIZE/2, ty = ch.y + CHAR_SIZE/2;
    let tDist = Math.hypot(tx - (e.x + ENEMY_SIZE/2), ty - (e.y + ENEMY_SIZE/2));
    g.allies.forEach(a => {
      const d = Math.hypot((a.x + CHAR_SIZE/2) - (e.x+ENEMY_SIZE/2), (a.y+CHAR_SIZE/2) - (e.y+ENEMY_SIZE/2));
      if (d < tDist) { tx = a.x + CHAR_SIZE/2; ty = a.y + CHAR_SIZE/2; tDist = d; }
    });
    const angle = Math.atan2(ty - (e.y+ENEMY_SIZE/2), tx - (e.x+ENEMY_SIZE/2));
    e.x += e.speed * Math.cos(angle);
    e.y += e.speed * Math.sin(angle);

    // Bullet collision
    let killed = false;
    if (g.lights) {
      // Firecracker: enemy dies if within 100px of any bullet; spawn firework at that bullet
      for (let bi = g.bullets.length - 1; bi >= 0; bi--) {
        const b = g.bullets[bi];
        const d = Math.hypot((e.x+ENEMY_SIZE/2) - b.x, (e.y+ENEMY_SIZE/2) - b.y);
        if (d <= 100) {
          g.fireworks.push({ x: b.x, y: b.y, timer: 0 });
          killed = true;
          break;
        }
      }
    } else {
      for (let bi = g.bullets.length - 1; bi >= 0; bi--) {
        const b = g.bullets[bi];
        if (rectsOverlap(e.x, e.y, ENEMY_SIZE, ENEMY_SIZE, b.x - BULLET_SIZE/2, b.y - BULLET_SIZE/2, BULLET_SIZE, BULLET_SIZE)) {
          g.bullets.splice(bi, 1);
          killed = true;
          break;
        }
      }
    }
    if (killed) {
      g.score++;
      g.lastEnemyLocation = [e.x, e.y];
      if (g.infected) g.allies.push(makeAlly(e.x, e.y));
      g.enemies.splice(i, 1);
      continue;
    }

    // Player collision
    if (rectsOverlap(e.x, e.y, ENEMY_SIZE, ENEMY_SIZE, ch.x, ch.y, CHAR_SIZE, CHAR_SIZE) && g.hitCooldown <= 0) {
      g.enemies.splice(i, 1);
      if (!g.invulnerable) {
        if (g.shields.length === 0) {
          g.hearts.pop();
        } else {
          g.shields.pop();
        }
        g.hitCooldown = 90;
      }
      continue;
    }

    // Ally collision
    for (let ai = g.allies.length - 1; ai >= 0; ai--) {
      const a = g.allies[ai];
      if (rectsOverlap(e.x, e.y, ENEMY_SIZE, ENEMY_SIZE, a.x, a.y, CHAR_SIZE, CHAR_SIZE)) {
        g.allies.splice(ai, 1);
        g.enemies.splice(i, 1);
        break;
      }
    }
  }

  // ── MOVE ALLIES (follow player at slower speed) ──
  g.allies.forEach(a => {
    if ((keys['w'] || keys['W']) && a.y > 0) a.y -= 1;
    if ((keys['s'] || keys['S']) && a.y < H - CHAR_SIZE) a.y += 1;
    if ((keys['a'] || keys['A']) && a.x > 0) a.x -= 1;
    if ((keys['d'] || keys['D']) && a.x < W - CHAR_SIZE) a.x += 1;
  });

  // ── HIT COOLDOWN ──
  if (g.hitCooldown > 0) g.hitCooldown--;

  // ── UPDATE POWERUP PICKUPS ──
  updatePickups(g, ch);

  // ── FIREWORKS ──
  g.fireworks = g.fireworks.filter(f => { f.timer++; return f.timer < 9; }); // ~150ms at 60fps

  // ── BOMB COUNTDOWN ──
  if (g.bombActive) {
    g.bombTimer++;
    if (g.bombTimer >= 300) { // 5000ms
      g.enemies = [];
      g.bombActive = false;
      g.bombTimer = 0;
    }
  }

  // ── GAME OVER ──
  if (g.hearts.length === 0) {
    g.state = 'gameover';
    if (g.score > highScore) highScore = g.score;
    setTimeout(() => showOverlay('gameover'), 600);
  }
}

function makeBullet(cx, cy, dir, g) {
  const isGold = g.invulnerable;
  return { x: cx, y: cy, dir, gold: isGold, lights: g.lights };
}

function moveBullet(b) {
  const spd = BULLET_SPEED;
  if (b.dir === 'up')    b.y -= spd;
  if (b.dir === 'down')  b.y += spd;
  if (b.dir === 'left')  b.x -= spd;
  if (b.dir === 'right') b.x += spd;
}

function makeEnemy(ch) {
  const side = ['top','bottom','left','right'][Math.floor(Math.random()*4)];
  let x, y;
  if (side === 'top')    { x = Math.random()*W; y = -ENEMY_SIZE; }
  if (side === 'bottom') { x = Math.random()*W; y = H; }
  if (side === 'left')   { x = -ENEMY_SIZE; y = Math.random()*H; }
  if (side === 'right')  { x = W; y = Math.random()*H; }
  return { x, y, speed: ENEMY_SPEED };
}

function makeAlly(x, y) { return { x, y }; }

function rectsOverlap(ax, ay, aw, ah, bx, by, bw, bh) {
  return ax < bx+bw && ax+aw > bx && ay < by+bh && ay+ah > by;
}

// ─────────────────────────────────────────────
// POWERUP LOGIC
// ─────────────────────────────────────────────
function randPos() {
  return { x: Math.random()*(W-ITEM_SIZE), y: Math.random()*(H-ITEM_SIZE) };
}

function spawnPowerup(g) {
  const idx = Math.floor(Math.random()*8) + 1;
  const p = randPos();
  const base = { ...p, size: ITEM_SIZE, active: false, spawnTick: g.tick };
  if (idx === 1) g.lightnings.push({ ...base, type: 'lightning' });
  if (idx === 2) g.cannons.push({ ...base, type: 'cannon' });
  if (idx === 3) g.bombs.push({ ...base, type: 'bomb', exploding: false });
  if (idx === 4) g.infections.push({ ...base, type: 'poison' });
  if (idx === 5 && g.shields.length < 3) g.barriers.push({ ...base, type: 'barrier' });
  if (idx === 6) g.stars.push({ ...base, type: 'star' });
  if (idx === 7) g.honeys.push({ ...base, type: 'honey' });
  if (idx === 8) g.firecrackers.push({ ...base, type: 'firecracker_u' });
}

function updatePickups(g, ch) {
  const cx = ch.x, cy = ch.y;
  const DESPAWN_TICKS = 420; // 7000ms at 60fps
  const ACTIVE_TICKS  = 300; // 5000ms at 60fps

  // Run expire/restore callbacks first, then filter dead items
  function processGroup(arr, onCollect, onExpire) {
    arr.forEach(p => {
      const age = g.tick - p.spawnTick;
      // Pickup
      if (!p.active && !p.dead && rectsOverlap(cx, cy, CHAR_SIZE, CHAR_SIZE, p.x, p.y, p.size, p.size)) {
        p.active = true;
        p.activeTick = g.tick;
        if (onCollect) onCollect(p);
      }
      // Expire after active duration
      if (p.active && !p.restored && g.tick - p.activeTick >= ACTIVE_TICKS) {
        if (onExpire) onExpire(p);
        p.restored = true;
        p.dead = true;
      }
      // Despawn if never picked up
      if (!p.active && age >= DESPAWN_TICKS) {
        p.dead = true;
      }
    });
    return arr.filter(p => !p.dead);
  }

  g.lightnings = processGroup(g.lightnings,
    p => { g.character.speed *= 2; },
    p => { g.character.speed /= 2; }
  );

  g.cannons = processGroup(g.cannons,
    p => { g.fourBullet = true; },
    p => { g.fourBullet = false; }
  );

  // Bombs: special — no onExpire here, detonation handled in update()
  g.bombs = processGroup(g.bombs,
    p => { p.exploding = true; g.bombActive = true; g.bombTimer = 0; },
    null
  );

  g.infections = processGroup(g.infections,
    p => { g.infected = true; },
    p => { g.infected = false; }
  );

  g.barriers = processGroup(g.barriers,
    p => {
      if (g.shields.length < 3) g.shields.push({ x: 20 + g.shields.length * 50, y: 20 });
    },
    null
  );

  g.stars = processGroup(g.stars,
    p => { g.character.saiyan = true; g.character.speed *= 2; g.fourBullet = true; g.invulnerable = true; },
    p => { g.character.saiyan = false; g.character.speed /= 2; g.fourBullet = false; g.invulnerable = false; }
  );

  g.honeys = processGroup(g.honeys,
    p => { g.slowed = true; },
    p => { g.slowed = false; }
  );

  g.firecrackers = processGroup(g.firecrackers,
    p => { g.lights = true; },
    p => { g.lights = false; }
  );
}

// ─────────────────────────────────────────────
// DRAW
// ─────────────────────────────────────────────
function draw() {
  const g = game;

  // Checkerboard background
  for (let row = 0; row < H/SQUARE; row++) {
    for (let col = 0; col < W/SQUARE; col++) {
      ctx.fillStyle = (row+col)%2===0 ? TAN : BROWN;
      ctx.fillRect(col*SQUARE, row*SQUARE, SQUARE, SQUARE);
    }
  }

  // Allies
  g.allies.forEach(a => ctx.drawImage(IMG.zombie, a.x, a.y, CHAR_SIZE, CHAR_SIZE));

  // Enemies
  g.enemies.forEach(e => ctx.drawImage(IMG.enemy, e.x, e.y, ENEMY_SIZE, ENEMY_SIZE));

  // Fireworks
  g.fireworks.forEach(f => ctx.drawImage(IMG.firework, f.x - 25, f.y - 25, 50, 50));

  // Bullets
  g.bullets.forEach(b => {
    let img;
    if (g.lights) {
      if (b.dir === 'up')    img = IMG.firecracker_u;
      if (b.dir === 'down')  img = IMG.firecracker_d;
      if (b.dir === 'left')  img = IMG.firecracker_l;
      if (b.dir === 'right') img = IMG.firecracker_r;
    } else {
      img = b.gold ? IMG.gold_bullet : IMG.bullet;
    }
    ctx.drawImage(img, b.x - BULLET_SIZE/2, b.y - BULLET_SIZE/2, BULLET_SIZE, BULLET_SIZE);
  });

  // Character
  if (g.hearts.length > 0) {
    const charImg = g.character.saiyan ? IMG.saiyan : IMG.agent;
    const blink = g.hitCooldown > 0 && Math.floor(g.hitCooldown/6)%2===1;
    if (!blink) ctx.drawImage(charImg, g.character.x, g.character.y, CHAR_SIZE, CHAR_SIZE);
  }

  // Powerup pickups
  drawPickups(g);

  // HUD: score
  ctx.font = 'bold 42px "Courier New", Courier, monospace';
  ctx.textAlign = 'center';
  ctx.textBaseline = 'top';
  // Pixel-style outline: 8 offset draws in a cross pattern
  ctx.fillStyle = '#000';
  ctx.fillText('Score: ' + g.score, W/2 - 2, 10);
  ctx.fillText('Score: ' + g.score, W/2 + 2, 10);
  ctx.fillText('Score: ' + g.score, W/2, 10 - 2);
  ctx.fillText('Score: ' + g.score, W/2, 10 + 2);
  ctx.fillText('Score: ' + g.score, W/2 - 2, 10 - 2);
  ctx.fillText('Score: ' + g.score, W/2 + 2, 10 - 2);
  ctx.fillText('Score: ' + g.score, W/2 - 2, 10 + 2);
  ctx.fillText('Score: ' + g.score, W/2 + 2, 10 + 2);
  // White fill on top
  ctx.fillStyle = '#ffffff';
  ctx.fillText('Score: ' + g.score, W/2, 10);

  // HUD: hearts
  g.hearts.forEach(h => ctx.drawImage(IMG.heart, h.x, h.y, ITEM_SIZE, ITEM_SIZE));

  // HUD: shields (top-left)
  g.shields.forEach((s, i) => ctx.drawImage(IMG.shield, 20 + i*50, 20, ITEM_SIZE, ITEM_SIZE));

  // Bomb countdown overlay
  if (g.bombActive) {
    const secsLeft = Math.max(0, 5 - Math.floor(g.bombTimer / 60));
    ctx.fillStyle = 'rgba(0,0,0,0.55)';
    ctx.fillRect(W/2 - 120, H/2 - 50, 240, 80);
    ctx.fillStyle = '#ff4444';
    ctx.font = 'bold 16px "Courier New", Courier, monospace';
    ctx.textAlign = 'center';
    ctx.textBaseline = 'middle';
    ctx.fillText(secsLeft + 's', W/2, H/2);
  }

  // Paused state not in original — omitting to stay faithful
}

function drawPickups(g) {
  function drawGroup(arr, key) {
    arr.forEach(p => {
      if (p.dead) return;
      let imgKey = key;
      if (key === 'bomb') imgKey = p.exploding ? 'bomb_exploding' : 'bomb';
      const img = IMG[imgKey];
      if (img) ctx.drawImage(img, p.x, p.y, p.size, p.size);
    });
  }
  drawGroup(g.lightnings, 'lightning');
  drawGroup(g.cannons, 'cannon');
  drawGroup(g.bombs, 'bomb');
  drawGroup(g.infections, 'poison');
  drawGroup(g.barriers, 'barrier');
  drawGroup(g.stars, 'star');
  drawGroup(g.honeys, 'honey');
  drawGroup(g.firecrackers, 'firecracker_u');
}

// ─────────────────────────────────────────────
// OVERLAY
// ─────────────────────────────────────────────
function showOverlay(type) {
  if (type === 'gameover') {
    overlay.querySelector('.overlay-title').textContent = 'Game Over';
    overlaySubtitle.textContent = 'Score: ' + game.score + '   |   Best: ' + highScore;
    overlayControls.innerHTML = 'Press <span>Enter</span> or click to restart';
    startBtn.textContent = 'Play Again';
  }
  overlay.classList.remove('hidden');
}

// ─────────────────────────────────────────────
// LOOP
// ─────────────────────────────────────────────
let lastTs = 0;
function loop(ts = 0) {
  animId = requestAnimationFrame(loop);
  if (ts - lastTs < 14) return; // ~60fps cap
  lastTs = ts;
  if (game && game.state === 'running') { update(); draw(); }
  else if (game && game.state === 'gameover') draw();
}

// ─────────────────────────────────────────────
// BOOT
// ─────────────────────────────────────────────
loadImages(() => {
  renderIconCanvases();
  // Draw idle checkerboard while on menu
  for (let row = 0; row < H/SQUARE; row++) {
    for (let col = 0; col < W/SQUARE; col++) {
      ctx.fillStyle = (row+col)%2===0 ? TAN : BROWN;
      ctx.fillRect(col*SQUARE, row*SQUARE, SQUARE, SQUARE);
    }
  }
});