const bells = new Audio('./sounds/bell.wav');
const playBtn = document.querySelector('.btn-play');
const pauseBtn = document.querySelector('.btn-pause');
const resetBtn = document.querySelector('.btn-reset');
const minuteInput = document.querySelector('.minute-input');
const minuteSpan = document.querySelector('.minutes');
const secondSpan = document.querySelector('.seconds');

let myInterval;
let totalSeconds = 0;
let state = true;

minuteInput.addEventListener('input', () => {
  const value = Math.max(minuteInput.value, 1);
  minuteSpan.textContent = value.toString().padStart(2, '0');
  totalSeconds = value * 60;
});

const appTimer = () => {
  if (state) {
    state = false;

    totalSeconds--;

    const updateSeconds = () => {
      const minutesLeft = Math.floor(totalSeconds / 60);
      const secondsLeft = totalSeconds % 60;

      if (secondsLeft < 10) {
        secondSpan.textContent = '0' + secondsLeft;
      } else {
        secondSpan.textContent = secondsLeft;
      }
      minuteSpan.textContent = minutesLeft.toString().padStart(2, '0');

      

      if (totalSeconds === 0) {
        bells.play();
        clearInterval(myInterval);
        state = true;
        document.querySelector('.pomo-message').textContent = 'Session Over';
      }
    };

    myInterval = setInterval(updateSeconds, 1000);
  }
};

playBtn.addEventListener('click', () => {
  appTimer();
  document.querySelector('.pomo-message').textContent = 'Working';
});

pauseBtn.addEventListener('click', () => {
  clearInterval(myInterval);
  state = true;
  document.querySelector('.pomo-message').textContent = 'Paused';
});

resetBtn.addEventListener('click', () => {
  const value = Math.max(minuteInput.value, 1);
  minuteSpan.textContent = value.toString().padStart(2, '0');
  totalSeconds = value * 60;
  playBtn.dataset.duration = value;
  clearInterval(myInterval);
  state = true;
  secondSpan.textContent = '00';
  document.querySelector('.pomo-message').textContent = 'Press Play to Begin';
});