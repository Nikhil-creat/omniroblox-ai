from contextlib import asynccontextmanager
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Depends, Header, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from .config import settings
from .groq_router import router
from .rag import rag
from . import agents

async def auth(x_api_key: str = Header(default="")):
    if settings.api_key and x_api_key != settings.api_key:
        raise HTTPException(401, "bad api key")

@asynccontextmanager
async def lifespan(app: FastAPI):
    await router.discover()
    rag.connect()
    yield

app = FastAPI(title="OmniRoblox AI", version="2.0", lifespan=lifespan)
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

class Spec(BaseModel):
    spec: str
    session: str = "default"

class ErrorLog(BaseModel):
    log: str
    code: str = ""

@app.get("/health")
async def health():
    return {"groq": router.status, "latency_ms": router.latency_ms,
            "fast_model": router.fast, "heavy_model": router.heavy,
            "models_detected": len(router.models), "vector_db": rag.status}

@app.post("/v1/build", dependencies=[Depends(auth)])
async def build(s: Spec):
    return await agents.build_feature(s.spec, s.session)

@app.post("/v1/patch", dependencies=[Depends(auth)])
async def patch(e: ErrorLog):
    return {"patch": await agents.patch_error(e.log, e.code)}

@app.post("/v1/ui", dependencies=[Depends(auth)])
async def ui(s: Spec):
    return {"luau": await agents.vision_to_ui(s.spec)}

@app.post("/v1/ingest", dependencies=[Depends(auth)])
async def ingest():
    return {"chunks": rag.ingest()}

@app.websocket("/ws")
async def ws(sock: WebSocket):
    await sock.accept()
    try:
        while True:
            data = await sock.receive_json()
            await sock.send_json({"stage": "planning"})
            res = await agents.build_feature(data["spec"], data.get("session", "default"))
            await sock.send_json({"stage": "done", **res})
    except WebSocketDisconnect:
        pass
