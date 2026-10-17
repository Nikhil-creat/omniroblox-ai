--!strict
-- Server-side token-bucket rate limiter + argument validation for RemoteEvents.
local Players = game:GetService("Players")
local RemoteGuard = {}

local buckets: { [Player]: { tokens: number, last: number } } = {}

function RemoteGuard.allow(player: Player, rate: number, burst: number): boolean
	local now = os.clock()
	local b = buckets[player] or { tokens = burst, last = now }
	b.tokens = math.min(burst, b.tokens + (now - b.last) * rate)
	b.last = now
	buckets[player] = b
	if b.tokens < 1 then return false end
	b.tokens -= 1
	return true
end

function RemoteGuard.bind(remote: RemoteEvent, rate: number, burst: number, validate: (...any) -> boolean, handler: (Player, ...any) -> ())
	remote.OnServerEvent:Connect(function(player, ...)
		if not RemoteGuard.allow(player, rate, burst) then return end
		if not validate(...) then return end
		handler(player, ...)
	end)
end

Players.PlayerRemoving:Connect(function(p) buckets[p] = nil end)
return RemoteGuard
