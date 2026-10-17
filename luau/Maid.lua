--!strict
export type Task = RBXScriptConnection | Instance | () -> ()
local Maid = {}
Maid.__index = Maid

function Maid.new()
	return setmetatable({ _tasks = {} :: { Task } }, Maid)
end

function Maid:Give(t: Task): Task
	table.insert(self._tasks, t)
	return t
end

function Maid:Clean()
	for _, t in self._tasks do
		if typeof(t) == "RBXScriptConnection" then t:Disconnect()
		elseif typeof(t) == "Instance" then t:Destroy()
		elseif type(t) == "function" then t() end
	end
	table.clear(self._tasks)
end

return Maid
