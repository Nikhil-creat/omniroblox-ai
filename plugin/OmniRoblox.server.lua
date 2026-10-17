--!strict
-- Studio plugin: sends a spec to the backend and inserts returned code as a Script.
-- Enable Game Settings > Security > Allow HTTP Requests.
local HttpService = game:GetService("HttpService")
local ServerScriptService = game:GetService("ServerScriptService")
local BASE = "http://localhost"

local toolbar = plugin:CreateToolbar("OmniRoblox")
local button = toolbar:CreateButton("Build", "Build from spec", "")

button.Click:Connect(function()
	local spec = "Create a server-authoritative coin pickup system with DataStore saving"
	local ok, res = pcall(function()
		return HttpService:RequestAsync({
			Url = BASE .. "/v1/build", Method = "POST",
			Headers = { ["Content-Type"] = "application/json" },
			Body = HttpService:JSONEncode({ spec = spec }),
		})
	end)
	if not ok or not res.Success then warn("OmniRoblox request failed") return end
	local data = HttpService:JSONDecode(res.Body)
	local s = Instance.new("Script")
	s.Name = "OmniGenerated"
	s.Source = data.code
	s.Parent = ServerScriptService
end)
