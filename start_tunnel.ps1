$subdomain = "smartbaholash"
# Clean up any existing logs
if (Test-Path "lt.log") { Remove-Item "lt.log" -Force }
if (Test-Path "lt_err.log") { Remove-Item "lt_err.log" -Force }

while ($true) {
    Write-Host "Starting localtunnel for $subdomain..."
    if (Test-Path "lt.log") { Remove-Item "lt.log" -Force }
    
    # Start localtunnel in background via cmd
    $process = Start-Process cmd -ArgumentList "/c", "npx -y localtunnel --port 3000 --subdomain $subdomain" -PassThru -NoNewWindow -RedirectStandardOutput "lt.log" -RedirectStandardError "lt_err.log"
    
    # Wait for connection to establish
    Start-Sleep -Seconds 6
    
    if (Test-Path "lt.log") {
        $content = Get-Content "lt.log" -Raw
        Write-Host "Current log: $content"
        if ($content -like "*$subdomain.loca.lt*") {
            Write-Host "Successfully bound to $subdomain!"
            # Wait for process to exit
            $process.WaitForExit()
        } else {
            Write-Host "Subdomain not bound (got random or error), killing process and retrying..."
            try {
                Stop-Process -Id $process.Id -Force -ErrorAction SilentlyContinue
            } catch {}
        }
    } else {
        Write-Host "Log not found, retrying..."
        try {
            Stop-Process -Id $process.Id -Force -ErrorAction SilentlyContinue
        } catch {}
    }
    
    Write-Host "Waiting 10 seconds before next attempt..."
    Start-Sleep -Seconds 10
}
