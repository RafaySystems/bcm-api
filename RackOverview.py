#!/usr/bin/env python3
import requests
import json
import sys

# BCM API endpoint
BCM_URL = "https://localhost:8081/json"

# Paths to your certificates
CERT_FILE = "/root/.cm/admin.pem"
KEY_FILE = "/root/.cm/admin.key"

def bcm_call(payload):
    """Helper to call BCM JSON API."""
    response = requests.post(
        BCM_URL,
        json=payload,
        cert=(CERT_FILE, KEY_FILE),
        verify=False  # disable SSL verification
    )
    response.raise_for_status()
    return response.json()

def get_rack_uuid_by_name(rack_name):
    """Find rack UUID by name using getRacks."""
    payload = {
        "service": "cmpart",
        "call": "getRacks"
    }
    racks = bcm_call(payload)
    for rack in racks:
        if rack.get("name") == rack_name:
            return rack.get("uuid")
    return None

def get_rack_overview(rack_uuid):
    """Get the full rack overview using rack UUID."""
    payload = {
        "service": "cmgui",
        "call": "getRackOverview",
        "args": [rack_uuid]
    }
    # BCM returns the GuiRackOverview directly, not wrapped in 'overview'
    return bcm_call(payload)

def main():
    if len(sys.argv) != 2:
        print(f"Usage: {sys.argv[0]} <rack_name>")
        sys.exit(1)

    rack_name = sys.argv[1]

    rack_uuid = get_rack_uuid_by_name(rack_name)
    if not rack_uuid:
        print(f"❌ Rack '{rack_name}' not found")
        sys.exit(1)

    print(f"✅ Found rack '{rack_name}' UUID: {rack_uuid}")

    overview = get_rack_overview(rack_uuid)
    print(json.dumps(overview, indent=2))

if __name__ == "__main__":
    main()
