$ErrorActionPreference = "Stop"

# Health check
Invoke-RestMethod -Uri "http://localhost:8000/health" -Method Get | ConvertTo-Json -Depth 5 | Write-Output

# Education flow via /agent/ask
$body = @{ 
  user_id = "u1"; 
  channel = "web"; 
  domain = "education"; 
  prompt = "Tengeneza mpango wa somo wa dakika 30 wa Hisabati darasa la 4 kuhusu kuzidisha"; 
  context = @{ grade = 4; subject = "Hisabati"; duration_minutes = 30; language = "sw" } 
} | ConvertTo-Json

Invoke-RestMethod -Uri "http://localhost:8000/agent/ask" -Method Post -ContentType "application/json" -Body $body | ConvertTo-Json -Depth 6 | Write-Output
