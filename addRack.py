#!/usr/bin/env python3
import requests
import sys
import uuid
import json

# Check for rack name argument
if len(sys.argv) < 2:
    print("Usage: python3 addRack.py <rack_name>")
    sys.exit(1)

rack_name = sys.argv[1]

# Generate a new UUID for the rack
rack_uuid = str(uuid.uuid4())

# Rack payload
rack = {
    "baseType": "Rack",
    "name": rack_name,
    "uuid": rack_uuid,  # generated UUID
    "xCoordinate": 10,  # make sure this does not collide
    "yCoordinate": 0,
    "height": 42,
    "width": 19,
    "depth": 34,
    "angle": 0,
    "inverted": False,
    "location": "",
    "building": "",
    "room": "",
    "row": "",
    "partNumber": "",
    "serialNumber": "",
    "model": "",
    "type": "",
    "notes": "",
    "twin": "00000000-0000-0000-0000-000000000000"
}

payload = {
    "service": "cmpart",
    "call": "addRack",
    "args": [rack, 0]  # force=0
}

url = "https://localhost:8081/json"
cert = ("/root/.cm/admin.pem", "/root/.cm/admin.key")

response = requests.post(url, json=payload, cert=cert, verify=False)

data = response.json()

if data.get("success"):
    print(f"✅ Rack '{rack_name}' added successfully with UUID: {rack_uuid}")
else:
    print(f"❌ Failed to add rack '{rack_name}'")
    print(json.dumps(data.get("validation"), indent=2))
