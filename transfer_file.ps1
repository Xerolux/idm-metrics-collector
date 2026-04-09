$base64 = Get-Content "C:\Users\basti\Documents\GitHub\idm-metrics-collector\models.py.base64" -Raw
$command = "echo '$base64' | base64 -d > /tmp/idm-fix/models.py"

$plinkPath = "C:\Users\basti\Downloads\plink.exe"
& $plinkPath -ssh root@192.168.178.52 -pw sebi2634 -batch -hostkey "ssh-ed25519 255 SHA256:pL6L6DOo8UItU9cbXEoWudkrCzpyApX8bmYBUvCCmI0" $command

Write-Output "File transferred successfully"