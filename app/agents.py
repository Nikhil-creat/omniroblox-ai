from .groq_router import router
from .rag import rag
from .memory import remember, recall

PLANNER = "You are a Roblox Planner. Split the feature into atomic ordered tasks. Define client/server boundaries, folder layout (ServerScriptService/ReplicatedStorage/StarterPlayerScripts) and DataStore schema. Numbered list."
CODER = "You are a Roblox Coder. Output strict-typed idiomatic Luau (--!strict), ModuleScripts, CollectionService, rate-limited RemoteEvents with server validation, Maid-style cleanup. Each file as a code block preceded by its path."
REVIEWER = "You are a Roblox security reviewer. List exploits (client authority, remote injection, missing type/range validation), memory leaks and perf issues. Then return the corrected code."
PATCHER = "You are a Luau debugger. Given an error log and code, isolate root cause and return the fixed block with short patch notes."

async def build_feature(spec: str, session: str = "default") -> dict:
    ctx = rag.retrieve(spec)
    hist = await recall(session)
    base = f"{spec}\n\nPrevious requests in this project:\n{hist}\n\nReference:\n{ctx}"
    plan = await router.chat("heavy", PLANNER, base)
    code = await router.chat("fast", CODER, f"Plan:\n{plan}\n\nReference:\n{ctx}")
    audit = await router.chat("heavy", REVIEWER, code)
    await remember(session, {"spec": spec})
    return {"models": {"fast": router.fast, "heavy": router.heavy}, "plan": plan, "code": code, "audit": audit}

async def patch_error(log: str, code: str = "") -> str:
    return await router.chat("heavy", PATCHER, f"ERROR:\n{log}\n\nCODE:\n{code}")

async def vision_to_ui(description: str) -> str:
    return await router.chat("fast", CODER + " Generate a ScreenGui hierarchy with UIListLayout, UIPadding and UIScale for auto-scaling.", description)
