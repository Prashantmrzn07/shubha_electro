Set-Location $PSScriptRoot

$pythonExe = ".\.venv\Scripts\python.exe"
if (-not (Test-Path $pythonExe)) {
    $pythonExe = "python"
    Write-Warning "Virtual environment .venv not found. Using system python."
}

# Free port 8000 if an old background python process is holding it
try {
    $connections = Get-NetTCPConnection -LocalPort 8000 -State Listen -ErrorAction SilentlyContinue
    if ($connections) {
        foreach ($conn in $connections) {
            $proc = Get-Process -Id $conn.OwningProcess -ErrorAction SilentlyContinue
            if ($proc -and $proc.ProcessName -like "*python*") {
                Write-Host "Releasing port 8000 from previous python process (PID $($proc.Id))..." -ForegroundColor Yellow
                Stop-Process -Id $proc.Id -Force -ErrorAction SilentlyContinue
            }
        }
        Start-Sleep -Milliseconds 600
    }
} catch {}

Write-Host "Checking and applying database migrations..." -ForegroundColor Cyan
& $pythonExe manage.py migrate

Write-Host "`n========================================================" -ForegroundColor Green
Write-Host " Shuba Electronics Shopping System is ready!" -ForegroundColor Green
Write-Host " URL: http://127.0.0.1:8000/" -ForegroundColor Yellow
Write-Host " Customer portal: http://127.0.0.1:8000/accounts/login/" -ForegroundColor Yellow
Write-Host " Admin portal: http://127.0.0.1:8000/accounts/admin-login/" -ForegroundColor Yellow
Write-Host " Press Ctrl+C to stop the server" -ForegroundColor Gray
Write-Host "========================================================`n" -ForegroundColor Green

& $pythonExe manage.py runserver 127.0.0.1:8000
