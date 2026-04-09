$plinkPath = "C:\Users\basti\Downloads\plink.exe"
$server = "192.168.178.52"
$password = "sebi2634"
$hostKey = "ssh-ed25519 255 SHA256:pL6L6DOo8UItU9cbXEoWudkrCzpyApX8bmYBUvCCmI0"

Write-Output "Updating idm-logger container with TELEMETRY_SHARED_TOKEN..."

# Stop the container
& $plinkPath -ssh root@$server -pw $password -batch -hostkey $hostKey "docker stop idm-logger"

# Remove the container
& $plinkPath -ssh root@$server -pw $password -batch -hostkey $hostKey "docker rm idm-logger"

# Recreate the container with the TELEMETRY_SHARED_TOKEN
Write-Output "Creating new container with TELEMETRY_SHARED_TOKEN..."
$envVars = "-e IDM_HOST=192.168.178.103 -e IDM_PORT=502 -e METRICS_URL=http://victoriametrics:8428/write -e INTERNAL_API_KEY=change_me_secure_key -e TELEMETRY_SHARED_TOKEN=COMMUNITY-CONTRIBUTOR-TOKEN-2026"

$createCommand = "docker run -d --name idm-logger --network idm-metrics-collector_default --restart unless-stopped --volume idm-logger-data:/app/data --volume idm-vm-data:/storage -p 5008:5000 --label com.centurylinklabs.watchtower.scope=idm-updates $envVars ghcr.io/xerolux/idm-metrics-collector:latest"

& $plinkPath -ssh root@$server -pw $password -batch -hostkey $hostKey $createCommand

Write-Output "Waiting for container to start..."
Start-Sleep -Seconds 10

Write-Output "Checking container status..."
& $plinkPath -ssh root@$server -pw $password -batch -hostkey $hostKey "docker logs idm-logger --tail 20"

Write-Output "Update complete!"