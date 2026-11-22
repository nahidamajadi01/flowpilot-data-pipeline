import os
import json
import requests
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

token = os.getenv("HUBSPOT_SERVICE_KEY")

if not token:
    raise ValueError("Missing HubSpot service key")

headers = {
    "Authorization": f"Bearer {token}"
}

output_dir = Path("data/raw")
output_dir.mkdir(parents=True, exist_ok=True)


def extract_records(object_type):
    records = []
    after = None

    while True:
        params = {
            "limit": 100
        }

        if after:
            params["after"] = after

        response = requests.get(
            f"https://api.hubapi.com/crm/v3/objects/{object_type}",
            headers=headers,
            params=params,
            timeout=30
        )

        response.raise_for_status()
        data = response.json()

        records.extend(data.get("results", []))

        after = data.get("paging", {}).get(
            "next", {}
        ).get("after")

        if not after:
            break

    return records


for object_type in ["companies", "contacts", "deals"]:
    records = extract_records(object_type)

    file_path = output_dir / f"{object_type}.json"

    with open(file_path, "w", encoding="utf-8") as file:
        json.dump(records, file, indent=2)

    print(f"{object_type}: {len(records)} records extracted")