from flask import Flask, request
from datetime import datetime

app = Flask(__name__)

# License database
licenses = {
    "AURA-TEST-12345": {
        "expires": "2030-12-31",
        "max_devices": 1,
        "devices": []
    },
    # Add more licenses here
}

@app.route('/')
def verify_license():
    key = request.args.get('key')
    device_id = request.args.get('device')
    today = datetime.now().date()
    
    if not key or key not in licenses:
        return "INVALID"
    
    license_data = licenses[key]
    expiry_date = datetime.strptime(license_data['expires'], '%Y-%m-%d').date()
    
    if expiry_date < today:
        return f"EXPIRED|{license_data['expires']}"
    
    # Device management
    if device_id and device_id not in license_data['devices']:
        if len(license_data['devices']) >= license_data['max_devices']:
            return f"DEVICE_LIMIT|{len(license_data['devices'])}|{license_data['max_devices']}"
        license_data['devices'].append(device_id)
    
    days_left = (expiry_date - today).days
    return f"VALID|{license_data['expires']}|{days_left}|{len(license_data['devices'])}|{license_data['max_devices']}"

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
