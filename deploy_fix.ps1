$plinkPath = "C:\Users\basti\Downloads\plink.exe"
$server = "192.168.178.52"
$password = "sebi2634"
$hostKey = "ssh-ed25519 255 SHA256:pL6L6DOo8UItU9cbXEoWudkrCzpyApX8bmYBUvCCmI0"

Write-Output "Starting ML service fix..."

# Step 1: Create the Python fix script directly on the server
$fixScript = @"
import sys

# Read the file
with open('/app/ml_service/models.py', 'r') as f:
    content = f.read()

# Fix 1: Add defensive checks in partial_fit method
old_partial_fit = '''    def partial_fit(self, data: Dict[str, Any]) -> None:
        with self._lock:
            for key, value in data.items():
                if not isinstance(value, (int, float)) or (
                    isinstance(value, float) and math.isnan(value)
                ):
                    continue
                if key not in self.n:
                    self.n[key] = 0
                    self.means[key] = 0.0
                    self.m2[key] = 0.0
                    self.vars[key] = 0.0
                self.n[key] += 1
                count = self.n[key]
                delta = value - self.means[key]
                self.means[key] += delta / count
                delta2 = value - self.means[key]
                self.m2[key] += delta * delta2
                self.vars[key] = self.m2[key] / count if count > 1 else 0.0'''

new_partial_fit = '''    def partial_fit(self, data: Dict[str, Any]) -> None:
        with self._lock:
            for key, value in data.items():
                if not isinstance(value, (int, float)) or (
                    isinstance(value, float) and math.isnan(value)
                ):
                    continue
                if key not in self.n:
                    self.n[key] = 0
                    self.means[key] = 0.0
                    self.m2[key] = 0.0
                    self.vars[key] = 0.0
                self.n[key] += 1
                count = self.n[key]
                delta = value - self.means[key]
                self.means[key] += delta / count
                delta2 = value - self.means[key]
                if key not in self.m2:
                    self.m2[key] = 0.0
                if key not in self.vars:
                    self.vars[key] = 0.0
                self.m2[key] += delta * delta2
                self.vars[key] = self.m2[key] / count if count > 1 else 0.0'''

content = content.replace(old_partial_fit, new_partial_fit)

# Fix 2: Add scaler_m2 to get_state method
old_get_state = '''            "scaler_vars": dict(self.scaler.vars),
            "scaler_n": dict(self.scaler.n),
            "ema_loss": self.ema_loss,'''

new_get_state = '''            "scaler_vars": dict(self.scaler.vars),
            "scaler_n": dict(self.scaler.n),
            "scaler_m2": dict(self.scaler.m2),
            "ema_loss": self.ema_loss,'''

content = content.replace(old_get_state, new_get_state)

# Fix 3: Add scaler_m2 loading in load_state method
old_load_state = '''        else:
            self.scaler.n = scaler_n
        self.ema_loss = state.get("ema_loss")'''

new_load_state = '''        else:
            self.scaler.n = scaler_n
        self.scaler.m2 = state.get("scaler_m2", {})
        self.ema_loss = state.get("ema_loss")'''

content = content.replace(old_load_state, new_load_state)

# Write the fixed content
with open('/app/ml_service/models.py', 'w') as f:
    f.write(content)

print("Fix applied successfully!")
"@

# Create the fix script on the server using echo commands
Write-Output "Creating fix script on server..."
$encodedScript = [Convert]::ToBase64String([System.Text.Encoding]::UTF8.GetBytes($fixScript))
& $plinkPath -ssh root@$server -pw $password -batch -hostkey $hostKey "echo $encodedScript | base64 -d > /tmp/fix_partial_fit.py"

# Execute the fix
Write-Output "Applying fix..."
& $plinkPath -ssh root@$server -pw $password -batch -hostkey $hostKey "docker exec idm-ml-service python /tmp/fix_partial_fit.py"

Write-Output "Restarting ML service..."
& $plinkPath -ssh root@$server -pw $password -batch -hostkey $hostKey "docker restart idm-ml-service"

Write-Output "Waiting for service to restart..."
Start-Sleep -Seconds 10

# Check service status
Write-Output "Checking service status..."
& $plinkPath -ssh root@$server -pw $password -batch -hostkey $hostKey "docker logs idm-ml-service --tail 20"

Write-Output "Fix complete!"