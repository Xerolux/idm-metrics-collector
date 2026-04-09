#!/bin/bash

# Script to fix ML service KeyError issue
echo "Starting ML service fix..."

# Backup current models.py
docker exec idm-ml-service cp /app/ml_service/models.py /app/ml_service/models.py.backup

# Create the fix for partial_fit method
cat << 'EOF' > /tmp/fix_partial_fit.py
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
EOF

# Copy the fix script to the container
docker cp /tmp/fix_partial_fit.py idm-ml-service:/tmp/fix_partial_fit.py

# Run the fix script in the container
docker exec idm-ml-service python /tmp/fix_partial_fit.py

echo "Fix complete. Restarting ML service..."

# Restart the ML service
docker restart idm-ml-service

echo "ML service restarted successfully!"

# Wait for service to be healthy
echo "Waiting for ML service to be healthy..."
sleep 10

# Check service health
if docker exec idm-ml-service python -c "import urllib.request; urllib.request.urlopen('http://localhost:8080/health', timeout=5)" 2>/dev/null; then
    echo "ML service is healthy!"
else
    echo "Warning: ML service health check failed, but fix was applied."
fi

echo "Done!"