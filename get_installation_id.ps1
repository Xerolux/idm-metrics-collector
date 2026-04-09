$plinkPath = "C:\Users\basti\Downloads\plink.exe"
$server = "192.168.178.52"
$password = "sebi2634"
$hostKey = "ssh-ed25519 255 SHA256:pL6L6DOo8UItU9cbXEoWudkrCzpyApX8bmYBUvCCmI0"

Write-Output "Getting installation_id from database..."

$pythonScript = @"
import sqlite3
conn = sqlite3.connect('/app/data/idm_logger.db')
cursor = conn.cursor()
cursor.execute('SELECT value FROM config WHERE key = "installation_id"')
result = cursor.fetchone()
print(result[0] if result else 'Not found')
conn.close()
"@

& $plinkPath -ssh root@$server -pw $password -batch -hostkey $hostKey "echo '$pythonScript' | docker exec -i idm-logger python3"