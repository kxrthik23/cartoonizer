# Cartoonizer — Deployment Guide

Two parts to deploy:
1. **Backend** → Render (free tier, Python/Flask)
2. **Frontend** → Cloudflare Pages (free, static HTML)

---

## Part 1 — Backend on Render

### 1. Push the backend to GitHub

```bash
cd backend/
git init
git add .
git commit -m "Initial cartoonizer backend"
# Create a new repo on GitHub, then:
git remote add origin https://github.com/KaeBee2003/cartoonizer-api.git
git push -u origin main
```

### 2. Deploy on Render

1. Go to https://render.com → **New** → **Web Service**
2. Connect your GitHub repo (`cartoonizer-api`)
3. Render auto-detects `render.yaml` — click **Deploy**
4. Wait ~3 min for the first build (installs OpenCV etc.)
5. Your backend URL will be: `https://cartoonizer-api.onrender.com`
   (or whatever name you chose — copy it from the Render dashboard)

> **Free tier note:** Render spins down after 15 min of inactivity.
> First request after idle takes ~10–30 sec to cold-start.
> You can add a free uptime monitor (e.g. UptimeRobot) to ping it every 10 min if you want it always warm.

---

## Part 2 — Frontend on Cloudflare Pages

### 1. Update the API URL

Open `frontend/index.html` and replace line:

```js
const API_BASE = "https://YOUR-APP-NAME.onrender.com";
```

with your actual Render URL, e.g.:

```js
const API_BASE = "https://cartoonizer-api.onrender.com";
```

### 2. Push frontend to GitHub

```bash
cd frontend/
git init
git add .
git commit -m "Initial cartoonizer frontend"
# Create a new repo on GitHub, then:
git remote add origin https://github.com/KaeBee2003/cartoonizer-web.git
git push -u origin main
```

### 3. Deploy on Cloudflare Pages

```bash
# Option A: via Wrangler CLI
npm install -g wrangler
wrangler login
cd frontend/
wrangler pages deploy . --project-name cartoonizer
```

Or via dashboard:
1. Go to https://dash.cloudflare.com → **Workers & Pages** → **Create** → **Pages**
2. Connect your GitHub repo (`cartoonizer-web`)
3. Build command: *(leave blank)*
4. Build output directory: `/`
5. Deploy!

Your site will be live at: `https://cartoonizer.pages.dev`

---

## CORS note

The backend's `app.py` already allows `*.pages.dev`.
If you add a custom domain later, add it to the `origins` list in `app.py`:

```python
CORS(app, origins=[
    ...
    "https://yourdomain.com",
])
```

---

## Local dev

```bash
# Backend
cd backend/
pip install -r requirements.txt
python app.py
# → running on http://localhost:5000

# Frontend — just open in browser
# (update API_BASE to http://localhost:5000 for local testing)
open frontend/index.html
```

---

## File structure

```
cartoonizer/
├── backend/
│   ├── app.py           ← Flask API
│   ├── requirements.txt
│   └── render.yaml      ← Render deploy config
└── frontend/
    ├── index.html       ← Full UI (single file)
    └── wrangler.toml    ← Cloudflare Pages config
```
