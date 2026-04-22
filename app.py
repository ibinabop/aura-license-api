from flask import Flask, request
from datetime import datetime
import json
import os

app = Flask(__name__)

LICENSE_FILE = 'licenses.json'
ADMIN_KEY = "AuraV6_Secret_Key_2024"

# Default licenses
DEFAULT_LICENSES = {
    "AURA-TEST-12345": {
        "user": "TestUser",
        "email": "test@test.com",
        "plan": "Test",
        "expires": "2030-12-31",
        "max_devices": 3,
        "devices": []
    },
    "AURA-A6240AA3-C90C73": {
        "user": "Aura",
        "email": "ibinaboosa@gmail.com",
        "plan": "Lifetime",
        "expires": "2099-12-31",
        "max_devices": 1,
        "devices": []
    },
    "AURA-877D0E9B-DDB7CD": {
        "user": "Aura",
        "email": "ibinaboosa@gmail.com",
        "plan": "Lifetime",
        "expires": "2099-12-31",
        "max_devices": 1,
        "devices": []
    }
}

def load_licenses():
    if os.path.exists(LICENSE_FILE):
        with open(LICENSE_FILE, 'r') as f:
            return json.load(f)
    save_licenses(DEFAULT_LICENSES)
    return DEFAULT_LICENSES

def save_licenses(licenses):
    with open(LICENSE_FILE, 'w') as f:
        json.dump(licenses, f, indent=2)

@app.route('/')
def verify_license():
    key = request.args.get('key')
    device_id = request.args.get('device')
    today = datetime.now().date()
    
    licenses = load_licenses()
    
    if not key or key not in licenses:
        return "INVALID"
    
    license_data = licenses[key]
    expiry_date = datetime.strptime(license_data['expires'], '%Y-%m-%d').date()
    
    if expiry_date < today:
        return f"EXPIRED|{license_data['expires']}"
    
    if device_id:
        if device_id not in license_data['devices']:
            if len(license_data['devices']) >= license_data['max_devices']:
                return f"DEVICE_LIMIT|{len(license_data['devices'])}|{license_data['max_devices']}"
            license_data['devices'].append(device_id)
            save_licenses(licenses)
    
    days_left = (expiry_date - today).days
    return f"VALID|{license_data['expires']}|{days_left}|{len(license_data['devices'])}|{license_data['max_devices']}"

@app.route('/stats')
def license_stats():
    admin_key = request.args.get('admin_key')
    if admin_key != ADMIN_KEY:
        return "Unauthorized"
    
    licenses = load_licenses()
    return json.dumps(licenses, indent=2)

@app.route('/reset')
def reset_licenses():
    admin_key = request.args.get('admin_key')
    if admin_key != ADMIN_KEY:
        return "Unauthorized"
    
    if os.path.exists(LICENSE_FILE):
        os.remove(LICENSE_FILE)
    
    load_licenses()
    return "Licenses reset successfully! New defaults loaded."

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
