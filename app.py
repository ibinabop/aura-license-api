from flask import Flask, request
from datetime import datetime
import json
import os

app = Flask(__name__)

LICENSE_FILE = 'licenses.json'

# Default licenses (will be saved to file)
DEFAULT_LICENSES = {
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
    # First run - create default licenses
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

@app.route('/add_license', methods=['POST'])
def add_license():
    """Admin endpoint to add licenses remotely"""
    admin_key = request.args.get('admin_key')
    if admin_key != 'YOUR_SECRET_KEY_HERE':
        return "Unauthorized"
    
    data = request.json
    licenses = load_licenses()
    licenses[data['key']] = {
        "user": data['user'],
        "email": data['email'],
        "plan": data['plan'],
        "expires": data['expires'],
        "max_devices": data['max_devices'],
        "devices": []
    }
    save_licenses(licenses)
    return "License added"

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
