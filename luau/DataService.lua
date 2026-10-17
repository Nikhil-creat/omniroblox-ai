--!strict
local DataStoreService = game:GetService("DataStoreService")
local Players = game:GetService("Players")
local store = DataStoreService:GetDataStore("PlayerData_v1")
local DataService = {}
local cache: { [number]: { [string]: any } } = {}
local DEFAULT = { coins = 0 }

local function retry<T>(fn: () -> T): (boolean, T?)
	for i = 1, 4 do
		local ok, res = pcall(fn)
		if ok then return true, res end
		task.wait(2 ^ i)
	end
	return false, nil
end

function DataService.load(player: Player)
	local ok, data = retry(function() return store:GetAsync(tostring(player.UserId)) end)
	cache[player.UserId] = if ok and data then data else table.clone(DEFAULT)
end

function DataService.save(player: Player)
	local d = cache[player.UserId]
	if not d then return end
	retry(function() return store:UpdateAsync(tostring(player.UserId), function() return d end) end)
	cache[player.UserId] = nil
end

function DataService.get(player: Player) return cache[player.UserId] end

Players.PlayerAdded:Connect(DataService.load)
Players.PlayerRemoving:Connect(DataService.save)
game:BindToClose(function() for _, p in Players:GetPlayers() do DataService.save(p) end end)
return DataService
