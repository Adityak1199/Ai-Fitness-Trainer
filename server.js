// server.js
const express = require('express');
const path = require('path');
const bodyParser = require('body-parser');
const { spawn } = require('child_process');
const app = express();
const PORT = 3000;

app.use(bodyParser.json());
app.use(express.static(path.join(__dirname, 'public')));

// Endpoint to start the Python trainer
app.post('/start', (req, res) => {
  const { exercise } = req.body;
  if (!exercise) {
    return res.status(400).json({ error: 'Missing exercise' });
  }

  // map from UI value to trainer.py argument
  let arg = '';
  if (exercise === 'bicep') arg = 'bicep_curl';
  else if (exercise === 'squat') arg = 'squat';
  else if (exercise === 'pushup') arg = 'push_up';
  else arg = exercise;

  // Use 'python' on Windows or 'python3' on Unix. Try to spawn python3, fall back to python.
  const pythonCmd = process.platform === 'win32' ? 'python' : 'python3';

  // Spawn the Python process
  const py = spawn(pythonCmd, ['trainer.py', arg], { cwd: __dirname });

  py.stdout.on('data', (data) => {
    console.log(`PYOUT: ${data.toString()}`);
  });

  py.stderr.on('data', (data) => {
    console.error(`PYERR: ${data.toString()}`);
  });

  py.on('close', (code) => {
    console.log(`Python process exited with code ${code}`);
  });

  // respond immediately that process has been started
  res.json({ status: 'started', exercise: arg });
});

app.listen(PORT, () => {
  console.log(`Server running on http://localhost:${PORT}`);
});
