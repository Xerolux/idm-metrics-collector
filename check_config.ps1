$plinkPath = "C:\Users\basti\Downloads\plink.exe"
$server = "192.168.178.52"
$password = "sebi2634"
$hostKey = "ssh-ed25519 255 SHA256:pL6L6DOo8UItU9cbXEoWudkrCzpyApX8bmYBUvCCmI0"

$pythonScript = @"
from idm_logger.config import config
print(f"installation_id: {config.get('installation_id')}")
print(f"telemetry.enabled: {config.get('telemetry.enabled', True)}")
print(f"telemetry.server_url: {config.get('telemetry.server_url', 'default')}")
print(f"hp_model: {config.get('hp_model', 'Unknown')}")
"@

Write-Output "Checking config..."
& $plinkPath -ssh root@$server -pw $password -batch -hostkey $hostKey "echo '$pythonScript' | docker exec -i idm-logger python"