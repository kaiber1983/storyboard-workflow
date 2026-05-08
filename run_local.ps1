$ErrorActionPreference = "Stop"
$env:HOST = if ($env:HOST) { $env:HOST } else { "127.0.0.1" }
$env:PORT = if ($env:PORT) { $env:PORT } else { "8787" }
python "$PSScriptRoot\storyboard_agent_server.py"
