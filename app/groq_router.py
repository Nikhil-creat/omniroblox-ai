import re, time, httpx
from .config import settings

SKIP = ("whisper", "guard", "tts", "playai", "embed")

class GroqRouter:
    """Detects live models at startup and maps them to fast/heavy roles."""
    def __init__(self):
        self.models: list[str] = []
        self.fast = self.heavy = None
        self.latency_ms: float | None = None
        self.status = "not_initialized"

    @staticmethod
    def _size(name: str) -> float:
        m = re.search(r"(\d+(?:\.\d+)?)b", name.lower())
        return float(m.group(1)) if m else 0.0

    async def discover(self):
        if not settings.groq_api_key:
            self.status = "no_api_key"; return
        t = time.perf_counter()
        try:
            async with httpx.AsyncClient(timeout=15) as c:
                r = await c.get(f"{settings.groq_base}/models",
                                headers={"Authorization": f"Bearer {settings.groq_api_key}"})
                r.raise_for_status()
            self.latency_ms = round((time.perf_counter() - t) * 1000, 1)
            self.models = [m["id"] for m in r.json()["data"]
                           if not any(s in m["id"].lower() for s in SKIP)]
            sized = sorted([m for m in self.models if self._size(m) > 0], key=self._size)
            pool = sized or self.models
            self.fast = pool[0] if pool else None
            self.heavy = pool[-1] if pool else None
            self.status = "online"
        except Exception as e:
            self.status = f"error: {e}"

    async def chat(self, role: str, system: str, user: str) -> str:
        model = self.heavy if role == "heavy" else self.fast
        if not model:
            raise RuntimeError(f"Groq unavailable ({self.status})")
        async with httpx.AsyncClient(timeout=90) as c:
            r = await c.post(f"{settings.groq_base}/chat/completions",
                headers={"Authorization": f"Bearer {settings.groq_api_key}"},
                json={"model": model, "temperature": 0.2,
                      "messages": [{"role": "system", "content": system},
                                   {"role": "user", "content": user}]})
            r.raise_for_status()
        return r.json()["choices"][0]["message"]["content"]

router = GroqRouter()
