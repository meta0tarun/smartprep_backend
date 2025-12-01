# SmartPrep Backend — Deployment Guide

## Prerequisites
- Docker installed (local build / Render uses Dockerfile)
- Supabase project 
- OpenRouter API key (if you want live LLM)
- Your hosting choice: Render, Railway, VPS, or Docker on VPS

## 1) Obtain full DATABASE_URL from Supabase
1. Open https://app.supabase.com and sign in.
2. Select your project (the one matching https://ocpldyafbkxuwxkznggj.supabase.co).
3. Go to **Settings → Database**.
4. Under "Connection string" copy the **URI** that looks like:
   `postgres://postgres:YOUR_DB_PASSWORD@db.xxxxxxxxx.supabase.co:5432/postgres`
5. This full string is your `DATABASE_URL`. Save it securely.

## 2) Local dev (optional)
- Create a `.env` file in the repo root:

DATABASE_URL=postgres://postgres:yourpassword@db:5432/smartprep
OPENROUTER_API_KEY=your_key_here # optional
DEMO_MODE=true # use stub LLM if you don't want OpenRouter usage

- Start docker-compose (local Postgres + backend):


docker-compose up --build

- Create DB tables:


docker exec -it <backend_container> python -m app.create_tables

- Test:


curl -F "file=@/path/to/sample.jpg" http://localhost:8000/analyze-llm


## 3) Deploy to Render / Railway (recommended quick path)
### Render
1. Create new Web Service in Render → connect GitHub repo.
2. Select "Docker" (it will use the repository Dockerfile).
3. In Environment → set Environment Variables:
 - `DATABASE_URL` = (value from Supabase step 1)
 - `OPENROUTER_API_KEY` = (your key) or leave blank and set `DEMO_MODE=true`
 - `DEMO_MODE` = "false" or "true"
 - `UPLOAD_DIR` = "/tmp/uploads"
4. Deploy. Render will build and run the container. The app listens on port 8000.

### Railway
Similar: create a new project, deploy Docker, add env vars.

## 4) Run create_tables on deployed container (one-time)
- If you can SSH into the container or use the provider's web console to run a command:


python -m app.create_tables

- Alternatively the tables can be created in Supabase SQL editor using the earlier SQL schema.

## 5) Set your Flutter app backend URL
Update `Constants.BACKEND_BASE_URL` in Flutter to:


https://<your-render-service>.onrender.com

or the domain provided by Railway.

## 6) Test full flow from a device
1. Install APK on device.
2. Make sure backend URL is reachable.
3. Upload a PDF or image and validate insights UI.

## Troubleshooting
- If you get 500 errors: check server logs (Render/ Railway logs). Paste exception trace into the console to fix.
- If OCR fails: verify container has `tesseract --version` and `pdftoppm` installed.
- If LLM errors: verify OPENROUTER_API_KEY and check response body in server logs.

## Security notes
- Do NOT store OPENROUTER_API_KEY in the mobile app.
- Keep DATABASE_URL private (set in container env variables).
- Use HTTPS in production.