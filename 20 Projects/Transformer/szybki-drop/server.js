const express = require('express');
const multer = require('multer');
const path = require('path');
const fs = require('fs');
const { v4: uuidv4 } = require('uuid');
const crypto = require('crypto');
const { Readable } = require('stream');

const app = express();
const PORT = 443;
const UPLOAD_DIR = path.join(__dirname, 'uploads');

if (!fs.existsSync(UPLOAD_DIR)) fs.mkdirSync(UPLOAD_DIR);

const storage = multer.diskStorage({
    destination: (req, file, cb) => cb(null, UPLOAD_DIR),
    filename: (req, file, cb) => cb(null, `${uuidv4()}-${file.originalname}`)
});
const upload = multer({ storage });

app.use(express.static('public'));

// --- ENDPOINTY APLIKACJI (Wgrywanie, info, pobieranie) ---
app.post('/upload', upload.single('file'), (req, res) => {
    if (!req.file) return res.status(400).send('Nie przesłano pliku.');
    const downloadLink = `${req.protocol}://${req.get('host')}/download/${req.file.filename}`;
    setTimeout(() => {
        fs.unlink(req.file.path, (err) => { if (!err) console.log(`[Info] Usunięto: ${req.file.path}`); });
    }, 60 * 60 * 1000);
    res.json({ link: downloadLink });
});

app.get('/download/:id', (req, res) => res.sendFile(path.join(__dirname, 'public', 'download.html')));

app.get('/api/info/:id', (req, res) => {
    const filePath = path.join(UPLOAD_DIR, req.params.id);
    if (fs.existsSync(filePath)) {
        res.json({ name: req.params.id.substring(37), size: fs.statSync(filePath).size });
    } else {
        res.status(404).json({ error: 'Plik nie istnieje lub już wygasł.' });
    }
});

app.get('/api/download/:id', (req, res) => {
    const filePath = path.join(UPLOAD_DIR, req.params.id);
    if (fs.existsSync(filePath)) res.download(filePath);
    else res.status(404).send('Plik nie istnieje.');
});

// --- ENDPOINTY TESTOWE (PING I PRAWDZIWY 10-SEKUNDOWY SPEEDTEST) ---

app.get('/api/ping', (req, res) => res.status(200).send('pong'));

// Download: Nieskończony strumień (do momentu aż klient sam nie przerwie połączenia)
app.get('/api/speedtest/download', (req, res) => {
    res.set({
        'Content-Type': 'application/octet-stream',
        'Cache-Control': 'no-store, no-cache, must-revalidate, private'
    });

    // Generujemy 128KB losowych danych raz w pamięci i wysyłamy je w kółko
    const chunk = crypto.randomBytes(128 * 1024); 
    
    const stream = new Readable({
        read() {
            this.push(chunk);
        }
    });

    stream.pipe(res);

    // Kiedy klient przerwie połączenie po 10 sek, ucinamy stream (żeby nie marnować zasobów)
    req.on('close', () => {
        stream.destroy();
    });
});

// Upload: Połyka wszystkie dane przychodzące od klienta i wyrzuca je w nicość
app.post('/api/speedtest/upload', (req, res) => {
    req.on('data', () => {}); 
    req.on('end', () => res.sendStatus(200));
});

app.listen(PORT, () => console.log(`Serwer Szybki Drop działa na porcie ${PORT}`));