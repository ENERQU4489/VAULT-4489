const express = require('express');
const http = require('http');
const { Server } = require('socket.io');
const pty = require('node-pty');
const os = require('os');
const path = require('path');
const cors = require('cors');

const app = express();
app.use(cors());

const server = http.createServer(app);
const io = new Server(server, {
  cors: {
    origin: "*",
    methods: ["GET", "POST"]
  }
});

const PORT = process.env.PORT || 3001;
const shell = os.platform() === 'win32' ? 'powershell.exe' : 'bash';

io.on('connection', (socket) => {
  console.log('Client connected:', socket.id);

  // Spawnowanie procesu gemini-cli
  // Zakładamy, że polecenie to po prostu 'gemini'
  // Używamy node-pty, aby zachować zachowanie terminala (kolory ANSI itp.)
  const ptyProcess = pty.spawn(shell, [], {
    name: 'xterm-color',
    cols: 80,
    rows: 30,
    cwd: process.cwd(),
    env: process.env
  });

  // Po uruchomieniu shella, wysyłamy komendę startową gemini
  // Robimy to po krótkim opóźnieniu, aby shell zdążył się podnieść
  setTimeout(() => {
    ptyProcess.write('gemini\r');
  }, 500);

  ptyProcess.onData((data) => {
    socket.emit('output', data);
  });

  socket.on('input', (data) => {
    ptyProcess.write(data + '\r');
  });

  socket.on('resize', (size) => {
    ptyProcess.resize(size.cols, size.rows);
  });

  socket.on('disconnect', () => {
    console.log('Client disconnected:', socket.id);
    ptyProcess.kill();
  });
});

server.listen(PORT, () => {
  console.log(`Backend bridge running on http://localhost:${PORT}`);
});
