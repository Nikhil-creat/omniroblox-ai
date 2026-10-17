# OmniRoblox AI (master)
Agentic Roblox Studio engine: Planner / Coder / Reviewer / Auto-Patch on Groq with dynamic model detection.

## Static demo (GitHub Pages)
`index.html` runs fully in the browser with your own Groq key.

## Full backend
1. cp .env.example .env  (set GROQ_API_KEY, API_KEY)
2. docker compose up --build
3. GET /health, POST /v1/build /v1/patch /v1/ui /v1/ingest, WS /ws (send X-API-Key if API_KEY set)
4. Install plugin/OmniRoblox.server.lua in Studio (set BASE url, add header X-API-Key).
5. luau/ has Maid, RemoteGuard, DataService templates. data/*.md is auto-ingested into Qdrant.

Designed & developed by Nikhil Chary Sriramoju
