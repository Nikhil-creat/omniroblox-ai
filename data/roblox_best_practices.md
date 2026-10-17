# Remotes
Never trust the client. Validate every RemoteEvent argument type and range on the server. Rate-limit per player with a token bucket. Never let the client send prices, damage or currency values.

Use RemoteFunction sparingly from server to client because a client can yield forever. Prefer RemoteEvent with explicit acknowledgements.

# Architecture
Put shared logic in ModuleScripts under ReplicatedStorage. Server only code lives in ServerScriptService. Use CollectionService tags for component based behaviour instead of scripts inside parts.

# Performance
Use task.wait, task.spawn and task.defer instead of wait and spawn. Avoid per frame loops on the server; prefer events. Use StreamingEnabled for large maps. Pool frequently created instances.

# DataStores
Wrap DataStore calls in pcall with retry and exponential backoff. Use UpdateAsync for read modify write. Save on PlayerRemoving and BindToClose. Keep session locks to prevent duplication.

# Memory
Disconnect connections and destroy instances when finished. Use a Maid or Janitor pattern. Clean per player tables on PlayerRemoving.

# UI
Use UIListLayout, UIPadding, UIAspectRatioConstraint and UIScale for responsive layout. Use Scale sizes instead of Offset where possible. Set ResetOnSpawn false for persistent ScreenGuis.
