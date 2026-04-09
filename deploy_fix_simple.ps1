$plinkPath = "C:\Users\basti\Downloads\plink.exe"
$server = "192.168.178.52"
$password = "sebi2634"
$hostKey = "ssh-ed25519 255 SHA256:pL6L6DOo8UItU9cbXEoWudkrCzpyApX8bmYBUvCCmI0"

# Read the local fixed models.py file
$localFile = "C:\Users\basti\Documents\GitHub\idm-metrics-collector\ml_service\models.py"
$base64Content = [Convert]::ToBase64String([IO.File]::ReadAllBytes($localFile))

# Send the base64 content to the server
$remoteCommand = "echo $base64Content > /tmp/models.py.b64"

Write-Output "Transferring fixed models.py to server..."
& $plinkPath -ssh root@$server -pw $password -batch -hostkey $hostKey $remoteCommand

# Decode the file in the container
Write-Output "Decoding file in container..."
& $plinkPath -ssh root@$server -pw $password -batch -hostkey $hostKey "docker exec idm-ml-service sh -c 'cat /tmp/models.py.b64 | base64 -d > /app/ml_service/models.py'"

Write-Output "Fix applied. Restarting ML service..."
& $plinkPath -ssh root@$server -pw $password -batch -hostkey $hostKey "docker restart idm-ml-service"

Write-Output "Waiting for service to restart..."
Start-Sleep -Seconds 15

Write-Output "Checking service status..."
& $plinkPath -ssh root@$server -pw $password -batch -hostkey $hostKey "docker logs idm-ml-service --tail 30"

Write-Output "Fix complete!"