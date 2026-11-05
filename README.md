# Try-On Anywear

A production-shaped virtual try-on web app: take or upload a photo, pick a garment, and get an
AI-generated picture of yourself wearing it. Built with FastAPI + Pillow on the backend and
Vite + vanilla TypeScript + Tailwind CSS on the frontend.

The app runs end to end **without any API key** using the built-in `MockProvider` (the result is
your photo with a clearly visible mock watermark). Switch one environment variable to use a real
model via Replicate (IDM-VTON) or Google Gemini.

## Features

- **Two input paths** — webcam capture with a 3-2-1 countdown, or photo upload. Push-to-camera
  stops the stream as soon as the frame is captured.
- **Six sample garments** plus upload. Selection by click, by keyboard, or by dragging a garment
  onto the photo stage.
- **Async job API** — `POST /api/try-on` returns a job id immediately; the UI polls status with a
  progress indicator, and can download the result or start over.
- **Rigorous image handling** — real byte-level format detection (JPEG/PNG/WebP), 5 MB cap,
  dimension bounds, decompression-bomb guard, auto-resize, EXIF/GPS stripping, transparency
  flattened to white.
- **Privacy by design** — images live in process memory only, inputs are dropped the moment a job
  finishes, everything expires after 10 minutes, and `DELETE /api/jobs/{id}` erases a job on
  demand.
- **Operational basics** — structured JSON logs with request ids, consistent JSON errors,
  per-IP rate limiting, CORS allowlist, provider timeouts and exponential-backoff retries.
- **Mobile-first UI** with light/dark mode, Uzbek (Latin) and English translations, visible focus
  states, ARIA labels and live regions.

## Quick start (mock provider, no API keys)

Requirements: Python 3.11+ and Node.js 20+.

### Backend
```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements-dev.txt
cp .env.example .env
uvicorn app.main:app --reload --port 8000
```

### Frontend
```bash
cd frontend
npm install
cp .env.example .env
npm run dev
```

Open http://localhost:3000

## Switching providers

Set `TRYON_PROVIDER=gemini` and `GEMINI_API_KEY=your_key` in backend/.env to use Gemini.
