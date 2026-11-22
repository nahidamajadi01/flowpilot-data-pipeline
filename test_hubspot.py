import os
import requests
from dotenv import load_dotenv

load_dotenv()

token = os.getenv("HUBSPOT_SERVICE_KEY")

if not token:
    raise ValueError("HubSpot service key missing from .env")

headers = {
    "Authorization": f"Bearer {token}"
}

for object_type in ["companies", "contacts", "deals"]:
    url = f"https://api.hubapi.com/crm/v3/objects/{object_type}"

    response = requests.get(
        url,
        headers=headers,
        params={"limit": 1},
        timeout=30
    )

    print("Status:", response.status_code)
    print("HubSpot response:", response.text)
    response.raise_for_status()

    data = response.json()

    print(f"SUCCESS: {object_type}")
    print(data["results"])