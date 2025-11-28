// script.js
document.addEventListener('DOMContentLoaded', () => {
  const startBtn = document.getElementById('startBtn');
  const welcome = document.getElementById('welcome');
  const choices = document.getElementById('choices');
  const status = document.getElementById('status');
  const statusText = document.getElementById('statusText');
  const backBtn = document.getElementById('backBtn');
  const okBtn = document.getElementById('okBtn');

  startBtn.addEventListener('click', () => {
    welcome.classList.add('hidden');
    choices.classList.remove('hidden');
  });

  backBtn.addEventListener('click', () => {
    choices.classList.add('hidden');
    welcome.classList.remove('hidden');
  });

  okBtn.addEventListener('click', () => {
    status.classList.add('hidden');
    welcome.classList.remove('hidden');
  });

  document.querySelectorAll('.exercise').forEach(btn => {
    btn.addEventListener('click', async (e) => {
      const ex = btn.getAttribute('data-ex');
      statusText.textContent = `Starting ${btn.textContent}...`;
      choices.classList.add('hidden');
      status.classList.remove('hidden');

      try {
        const response = await fetch('/start', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ exercise: ex })
        });
        const data = await response.json();
        if (data.error) {
          statusText.textContent = 'Failed to start: ' + data.error;
        } else {
          statusText.textContent = `Python process started for ${data.exercise}. Check the server terminal for logs and the webcam window for the tracker. Press 'q' in the tracker window to quit.`;
        }
      } catch (err) {
        statusText.textContent = 'Error connecting to server. Is the Node server running?';
      }
    });
  });
});
