$plinkPath = "C:\Users\basti\Downloads\plink.exe"
$server = "192.168.178.52"
$password = "sebi2634"
$hostKey = "ssh-ed25519 255 SHA256:pL6L6DOo8UItU9cbXEoWudkrCzpyApX8bmYBUvCCmI0"

Write-Output "Starting ML service fix..."

# Create a Python script inline and execute it
$pythonScript = @"
import re

with open('/app/ml_service/models.py', 'r') as f:
    content = f.read()

# Fix 1: Add defensive checks before accessing self.m2[key]
# Find the line: self.m2[key] += delta * delta2
# And add defensive checks before it

old_pattern = r"(                self\.n\[key\] \+= 1\s+count = self\.n\[key\]\s+delta = value - self\.means\[key\]\s+self\.means\[key] \+= delta / count\s+delta2 = value - self\.means\[key\]\s+)                self\.m2\[key\] \+= delta \* delta2"

new_code = r"\1                if key not in self.m2:\n                    self.m2[key] = 0.0\n                if key not in self.vars:\n                    self.vars[key] = 0.0\n                self.m2[key] += delta * delta2"

content = re.sub(old_pattern, new_code, content)

# Fix 2: Add scaler_m2 to get_state
content = content.replace(
    '            "scaler_vars": dict(self.scaler.vars),\n            "scaler_n": dict(self.scaler.n),\n            "ema_loss": self.ema_loss,',
    '            "scaler_vars": dict(self.scaler.vars),\n            "scaler_n": dict(self.scaler.n),\n            "scaler_m2": dict(self.scaler.m2),\n            "ema_loss": self.ema_loss,'
)

# Fix 3: Load scaler_m2 in load_state
content = content.replace(
    '        else:\n            self.scaler.n = scaler_n\n        self.ema_loss = state.get("ema_loss")',
    '        else:\n            self.scaler.n = scaler_n\n        self.scaler.m2 = state.get("scaler_m2", {})\n        self.ema_loss = state.get("ema_loss")'
)

with open('/app/ml_service/models.py', 'w') as f:
    f.write(content)

print("Fix applied successfully!")
"@

# Create the Python script file on the server
Write-Output "Creating fix script on server..."
$command = "cat > /tmp/fix_ml.py << 'ENDOFFILE'$pythonScript`nENDOFFILE"
& $plinkPath -ssh root@$server -pw $password -batch -hostkey $hostKey $command

# Execute the fix
Write-Output "Applying fix..."
& $plinkPath -ssh root@$server -pw $password -batch -hostkey $hostKey "python /tmp/fix_ml.py"

Write-Output "Restarting ML service..."
& $plinkPath -ssh root@$server -pw $password -batch -hostkey $hostKey "docker restart idm-ml-service"

Write-Output "Waiting for service to restart..."
Start-Sleep -Seconds 15

# Check service status
Write-Output "Checking service status..."
& $plinkPath -ssh root@$server -pw $password -batch -hostkey $hostKey "docker logs idm-ml-service --tail 30"

Write-Output "Fix complete!"