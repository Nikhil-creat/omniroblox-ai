import hashlib, math, re, pathlib
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct
from .config import settings

COLLECTION = "roblox_docs"
DIM = 256
DATA = pathlib.Path(__file__).resolve().parent.parent / "data"

def embed(text: str) -> list[float]:
    """Dependency-free hashing embedding (swap for a real model later)."""
    v = [0.0] * DIM
    for tok in re.findall(r"[a-z0-9_]+", text.lower()):
        v[int(hashlib.md5(tok.encode()).hexdigest(), 16) % DIM] += 1.0
    n = math.sqrt(sum(x * x for x in v)) or 1.0
    return [x / n for x in v]

def chunks(text: str, size: int = 700):
    parts, buf = [], ""
    for para in text.split("\n\n"):
        if len(buf) + len(para) > size and buf:
            parts.append(buf.strip()); buf = ""
        buf += para + "\n\n"
    if buf.strip():
        parts.append(buf.strip())
    return parts

class RAG:
    def __init__(self):
        self.client = None
        self.status = "offline"
        self.count = 0

    def connect(self):
        try:
            self.client = QdrantClient(url=settings.qdrant_url, timeout=5)
            names = [c.name for c in self.client.get_collections().collections]
            if COLLECTION not in names:
                self.ingest()
            self.count = self.client.count(COLLECTION).count
            self.status = f"synced ({self.count} chunks)"
        except Exception as e:
            self.status = f"offline: {e}"

    def ingest(self) -> int:
        if self.client is None:
            raise RuntimeError("Qdrant not connected")
        self.client.recreate_collection(COLLECTION, vectors_config=VectorParams(size=DIM, distance=Distance.COSINE))
        pts, i = [], 0
        for f in sorted(DATA.glob("*.md")):
            for c in chunks(f.read_text(encoding="utf-8")):
                pts.append(PointStruct(id=i, vector=embed(c), payload={"text": c, "source": f.name})); i += 1
        if pts:
            self.client.upsert(COLLECTION, pts)
        self.count = i
        self.status = f"synced ({i} chunks)"
        return i

    def retrieve(self, query: str, k: int = 4) -> str:
        if self.client is None:
            return "Use --!strict, server-authoritative remotes, task library."
        try:
            hits = self.client.search(COLLECTION, query_vector=embed(query), limit=k)
            return "\n---\n".join(h.payload["text"] for h in hits)
        except Exception:
            return "Use --!strict, server-authoritative remotes, task library."

rag = RAG()
