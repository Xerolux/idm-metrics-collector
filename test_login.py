import sys
import json
import sqlite3
import os

sys.path.append('.')

# Setup necessary envs to pass app init
os.environ["IDM_HOST"] = "127.0.0.1"
os.environ["IDM_PORT"] = "502"
os.environ["METRICS_URL"] = "http://localhost:8428"
os.environ["WEB_WRITE_ENABLED"] = "true"

from idm_logger.web import app
from idm_logger.config import config

config.data["idm"]["host"] = "127.0.0.1"
config.data["idm"]["port"] = 502
config.save()
config.reload()

# Make sure admin hash is set up from testing earlier or set anew
config.set_admin_password("admin")

print(f"Current config admin hash: {config.data['web'].get('admin_password_hash')}")
print(f"Admin check: {config.check_admin_password('admin')}")

with app.test_client() as client:
    # 1. Test Login with Admin
    print("\n--- Test Login admin ---")
    resp = client.post('/api/auth/login', json={"password": "admin"})
    print("Response status:", resp.status_code)
    print("Response JSON:", resp.get_json())

    # 2. Test Reset Password
    print("\n--- Test Reset Password ---")
    resp_reset = client.post('/api/auth/reset_password', json={
        "idm_host": "127.0.0.1",
        "idm_port": 502,
        "new_password": "newpassword123"
    })
    print("Reset status:", resp_reset.status_code)
    print("Reset JSON:", resp_reset.get_json())

    # 3. Test Login with New Password
    print("\n--- Test Login newpassword123 ---")
    resp_new = client.post('/api/auth/login', json={"password": "newpassword123"})
    print("Response status:", resp_new.status_code)
    print("Response JSON:", resp_new.get_json())

    # 4. Test Login with Admin again (should fail)
    print("\n--- Test Login admin (should fail) ---")
    resp_admin = client.post('/api/auth/login', json={"password": "admin"})
    print("Response status:", resp_admin.status_code)
    print("Response JSON:", resp_admin.get_json())
