import express from "express"
import path from "path"
import { fileURLToPath } from 'url';
import fs from "fs"
import puppeteer from "puppeteer"

const app = express()
const route = express.Router()

const __filename = fileURLToPath(import.meta.url)
const __dirname = path.dirname(__filename)
const DATA_DIR = path.join(__dirname, "data");
const FLIGHT_FILE = path.join(DATA_DIR, "flight.json");
const RES_FILE = path.join(DATA_DIR, "reservations.json");

// FLAG 설정
const FLAG = process.env.FLAG || "Whois2025{NULL_FLAG}";

// 미들웨어 설정
app.use(express.json());
app.use(express.urlencoded({ extended: true }));
app.use(express.static(path.join(__dirname)));
app.use('/api', route)

let seats
let nextReservationId = 0;

// 데이터 디렉토리 생성
if (!fs.existsSync(DATA_DIR)) {
    fs.mkdirSync(DATA_DIR, { recursive: true });
}

try{
    let seatsjson = fs.readFileSync(RES_FILE, 'utf-8')
    if(!seatsjson){
        seats = Array.from({ length: 12 }, () => Array(6).fill(null))
        nextReservationId = 0;
        fs.writeFileSync(RES_FILE, JSON.stringify({ seats, nextReservationId }, null, 2))
    }
    else{
        const data = JSON.parse(seatsjson)
        seats = data.seats
        nextReservationId = data.nextReservationId || 0
    }
}catch(e){
    seats = Array.from({ length: 12 }, () => Array(6).fill(null))
    nextReservationId = 0;
}

console.log("Seats initialized:", seats.length, "rows")
console.log("Next reservation ID:", nextReservationId)
console.log("FLAG:", FLAG)

function seatPatternOK(seat) {
    return /^\d{1,9}[A-Z]$/.test(String(seat).toUpperCase().trim());
}

function tryReserveSeat(rowIndex, colIndex, reservation) {
    if (seats[rowIndex][colIndex]) {
        return false
    }
    try{
        seats[rowIndex][colIndex] = reservation
        const dataToSave = { seats, nextReservationId };
        fs.writeFileSync(RES_FILE, JSON.stringify(dataToSave, null, 2))
    }catch(e){
        console.error("Failed to save reservation:", e)
        return false
    }
    return true
}

route.get('/flight', (req, res)=>{
    try {
        const flight = fs.readFileSync(FLIGHT_FILE, 'utf-8')
        const flightjson = JSON.parse(flight)
        res.status(200).json(flightjson)
    } catch(e) {
        res.status(500).json({ message: 'Failed to read flight data' })
    }
})

route.post('/reservations', (req, res)=>{
    const name = String(req.body.name || '').trim()
    const seat = String(req.body.seat || '').toUpperCase().trim()

    console.log("Reservation attempt - name:", name, "seat:", seat)
    
    // XSS 취약점: 이름 검증 부족 - HTML 태그가 그대로 저장됨
    if (!name || !seat || name.length < 2 || !seatPatternOK(seat)) {
        return res.status(400).json({ message: '잘못된 입력입니다. 이름(2글자 이상), 좌석(예: 7B)' })
    }

    const rowNumber = parseInt(seat.slice(0, -1), 10)
    const colLetter = seat.slice(-1)
    
    if (rowNumber < 1 || rowNumber > 12) {
        return res.status(400).json({ message: '좌석 행 범위는 1~12 입니다.' })
    }
    const colIndex = 'ABCDEF'.indexOf(colLetter)
    if (colIndex === -1) {
        return res.status(400).json({ message: '좌석 열은 A~F 입니다.' })
    }
    const rowIndex = rowNumber - 1

    const reservation = {
        id: ++nextReservationId,
        name,  // XSS 취약점: sanitize 하지 않고 그대로 저장
        seat,
        ts: new Date().toISOString()
    }

    const ok = tryReserveSeat(rowIndex, colIndex, reservation)
    if (!ok) {
        --nextReservationId;
        return res.status(409).json({ message: '이미 예약된 좌석입니다.' })
    }

    return res.status(201).json(reservation)
})

route.get('/reservations', (req, res)=>{
    const reservations = []
    for (let r = 0; r < seats.length; r++){
        for (let c = 0; c < seats[r].length; c++){
            const item = seats[r][c]
            if (item) reservations.push(item)
        }
    }
    return res.status(200).json(reservations)
})

route.delete('/reservations', (req, res)=>{
    const seat = req.query.id;
    if(!seat){
        return res.status(400).json({message:"No query"})
    }

    console.log("Delete request for seat:", seat);
    const rowNumber = parseInt(seat.slice(0, -1), 10)
    const colLetter = seat.slice(-1)
    const colIndex = 'ABCDEF'.indexOf(colLetter)
    const rowIndex = rowNumber - 1

    if (isNaN(rowIndex) || colIndex === -1 || !seats[rowIndex] || seats[rowIndex][colIndex] === undefined) {
        return res.status(400).json({ message: '유효하지 않은 좌석입니다.' });
    }

    if(!seats[rowIndex][colIndex]){
        return res.status(404).json({message:"해당 예약이 없습니다."})
    }
    seats[rowIndex][colIndex] = null
    try{
        const dataToSave = { seats, nextReservationId };
        fs.writeFileSync(RES_FILE, JSON.stringify(dataToSave, null, 2))
    }catch(e){
        return res.status(500).json({ message: '파일 저장 실패' });
    }
    return res.status(200).json({message:"success"})
})

// Admin Bot - Report 기능
app.get('/report', async (req, res) => {
    try {
        const path = req.query.path;

        if (!path) {
            return res.status(400).send('path is required');
        }

        console.log("Admin bot visiting:", path);

        const browser = await puppeteer.launch({ 
            headless: true,
            executablePath: process.env.CHROMIUM_PATH || '/usr/bin/chromium',
            args: [
                '--no-sandbox',
                '--disable-setuid-sandbox',
                '--disable-dev-shm-usage',
                '--disable-gpu'
            ]
        });

        const page = await browser.newPage();
        
        // FLAG를 쿠키에 설정
        await page.setCookie({
            name: 'flag',
            value: FLAG,
            domain: 'localhost',
            path: '/',
            httpOnly: false,
        });

        // 사용자가 지정한 페이지 방문
        const url = `http://localhost:8000/${path}`;
        console.log("Visiting URL:", url);
        
        await page.goto(url, { 
            waitUntil: 'networkidle2',
            timeout: 5000 
        });

        // 페이지에서 3초 대기 (XSS 실행 시간 확보)
        await page.waitForTimeout(3000);

        await browser.close();
        
        res.send('Admin visited the page');
    } catch (error) {
        console.error("Report error:", error);
        res.status(400).send('error: ' + error.message);
    }
});

app.use((err, req, res, next)=>{
    console.error(err.stack)
    res.status(500).json({ error: 'Internal Server Error' })
})

const PORT = process.env.PORT || 8000;

app.listen(PORT, '0.0.0.0', ()=>{
    console.log(`Server running on http://0.0.0.0:${PORT}`)
    console.log("CTF Challenge: Airline Reservation XSS with Bot")
})