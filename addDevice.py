#!/usr/bin/env python3
import requests
import json
import uuid
import urllib3
import sys

# Disable warnings for self-signed certificates
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# API endpoint and certs
API_URL = "https://localhost:8081/json"
CERT = "/root/.cm/admin.pem"
KEY = "/root/.cm/admin.key"

def call_cm_api(payload):
    resp = requests.post(API_URL, cert=(CERT, KEY), headers={"Content-Type": "application/json"},
                         data=json.dumps(payload), verify=False)
    return resp.json()

def get_rack_uuid(rack_name):
    payload = {
        "service": "cmpart",
        "call": "getRacks"
    }
    resp = call_cm_api(payload)
    for rack in resp:
        if rack.get("name") == rack_name:
            return rack.get("uuid")
    return None

def add_device(hostname, mac, ip, interface_name, rack_name):
    rack_uuid = get_rack_uuid(rack_name)
    if not rack_uuid:
        print(f"❌ Rack '{rack_name}' not found")
        return

    device_uuid = str(uuid.uuid4())
    interface_uuid = str(uuid.uuid4())

    payload = {
        "service": "cmdevice",
        "call": "addDevice",
        "args": [
            {
                "baseType": "Device",
                "uuid": device_uuid,
                "childType": "PhysicalNode",
                "hostname": hostname,
                "mac": mac,
                "partition": "57d8cd2a-fb37-4fa5-aceb-25787c6d3638",
                "category": "ba2aadc5-d8df-45fc-a246-5995c35273d3",
                "managementNetwork": "b510cb9a-f7d8-465b-aea0-968a610e0de5",
                "interfaces": [
                    {
                        "uuid": interface_uuid,
                        "baseType": "NetworkInterface",
                        "childType": "NetworkPhysicalInterface",
                        "name": interface_name,
                        "mac": mac,
                        "ip": ip,
                        "network": "b510cb9a-f7d8-465b-aea0-968a610e0de5",
                        "startIf": "ALWAYS",
                        "bringupduringinstall": "NO"
                    }
                ],
                "provisioningInterface": interface_uuid,
                "rackPosition": {
                    "baseType": "RackPosition",
                    "rack": rack_uuid,
                    "position": 1,
                    "height": 1
                }
            },
            1
        ]
    }

    resp = call_cm_api(payload)
    if resp.get("success"):
        device = resp.get("updated_entity")
        print(f"✅ Device '{hostname}' added successfully!")
        print("Full details:")
        print(json.dumps(device, indent=4))
        # Optionally, print main info
        print(f"\nHostname: {device.get('hostname')}")
        print(f"Device UUID: {device.get('uuid')}")
        interface = device.get("interfaces")[0]
        print(f"IP Address: {interface.get('ip')}")
        rack_pos = device.get("rackPosition")
        print(f"Rack UUID: {rack_pos.get('rack')}, Position: {rack_pos.get('position')}, Height: {rack_pos.get('height')}")
    else:
        print(f"❌ Failed to add device '{hostname}'")
        print(json.dumps(resp.get("validation"), indent=4))

if __name__ == "__main__":
    if len(sys.argv) != 6:
        print(f"Usage: {sys.argv[0]} <hostname> <mac> <ip> <interface_name> <rack_name>")
        sys.exit(1)
    
    hostname, mac, ip, interface_name, rack_name = sys.argv[1:]
    add_device(hostname, mac, ip, interface_name, rack_name)
