import requests
import json
import getpass
from collections import defaultdict
from itertools import combinations

# Ask for the platform selection
print("\nOptions: US1, US2, US3, US4, UK, EU1, EU2, EU3, IN, CA, AE, AU, KSA\n")
platform = input("What platform is your account on? ").upper()

# Define gateway URLs for each platform
gateway_urls = {
    "US1": "https://gateway.qg1.apps.qualys.com",
    "US2": "https://gateway.qg2.apps.qualys.com",
    "US3": "https://gateway.qg3.apps.qualys.com",
    "US4": "https://gateway.qg4.apps.qualys.com",
    "UK": "https://gateway.qg1.apps.qualys.co.uk",
    "EU1": "https://gateway.qg1.apps.qualys.eu",
    "EU2": "https://gateway.qg2.apps.qualys.eu",
    "EU3": "https://gateway.qg3.apps.qualys.it",
    "IN": "https://gateway.qg1.apps.qualys.in",
    "CA": "https://gateway.qg1.apps.qualys.ca",
    "AE": "https://gateway.qg1.apps.qualys.ae",
    "AU": "https://gateway.qg1.apps.qualys.com.au",
    "KSA": "https://gateway.qg1.apps.qualysksa.com"
}

# Select the correct gateway URL
if platform in gateway_urls:
    gateway_url = gateway_urls[platform]
else:
    print("Invalid platform selection. Exiting")
    exit(1)  # Exit if platform detail is incorrect

# Input for username and password at runtime
username = input("Enter your username: ")
password = getpass.getpass("Enter your password: ")

# Define the authentication URL using the gateway URL
auth_url = f"{gateway_url}/auth"

# Authentication headers and data for JWT
auth_headers = {
    "Content-Type": "application/x-www-form-urlencoded"
}
auth_data = {
    "username": username,
    "password": password,
    "token": "true"
}

# Perform authentication to get JWT
auth_response = requests.post(auth_url, headers=auth_headers, data=auth_data)
if auth_response.status_code != 201:
    print(f"Authentication failed. (HTTP {auth_response.status_code}).")
    print("Response from server:")
    print(auth_response.text or "No additional error details provided.")
    exit(1)

# Extract JWT token from response body (plain string)
jwt_token = auth_response.text.strip()
print("\nAuthentication successful.")

# Now fetch all assets using the asset endpoint
asset_url = f"{gateway_url}/rest/2.0/search/am/asset"
asset_headers = {
    "Accept": "application/json",
    "Authorization": f"Bearer {jwt_token}",
    "Content-Type": "application/json"
}

print("\nFetching assets...")

all_assets = []
last_seen_asset_id = None
has_more = True
page_size = 300  # Max allowed for fewer calls

while has_more:
    params = {"pageSize": page_size}
    if last_seen_asset_id:
        params["lastSeenAssetId"] = last_seen_asset_id
    
    asset_response = requests.post(asset_url, headers=asset_headers, params=params, json={})
    
    if asset_response.status_code != 200:
        print(f"Failed to fetch assets (HTTP {asset_response.status_code}).")
        print("Response from server:")
        print(asset_response.text or "No additional error details provided.")
        exit(1)
    
    data = asset_response.json()
    assets = data.get("assetListData", {}).get("asset", [])
    all_assets.extend(assets)
    
    current_has_more = data.get("hasMore", 0) == 1
    current_last_seen = data.get("lastSeenAssetId")
    
    print(f"\nFetched {len(all_assets)} assets so far...")
    
    has_more = current_has_more
    last_seen_asset_id = current_last_seen

# Check for potential duplicates across multiple fields
print("\nChecking for potential duplicates...\n")

# Track flagged duplicate pairs (as frozensets of asset IDs) to avoid repeats
flagged_pairs = set()

# Field display names and getters
fields = [
    ("assetName", "Asset name", lambda x: str(x.get("assetName") or "").strip().lower()),
    ("dnsName", "DNS name", lambda x: str(x.get("dnsName") or "").strip().lower()),
    ("netBIOSName", "NetBIOS name", lambda x: str(x.get("netBIOSName") or "").strip().lower()),
    ("macAddress", "MAC address", lambda x: str(x.get("macAddress") or "").strip().lower()),
    ("ipv4Address", "IPv4 address", lambda x: str(x.get("address") or "").strip())
]

for field_name, display_name, normalize_func in fields:
    groups = defaultdict(list)
    for asset in all_assets:
        value = normalize_func(asset)
        if value:  # Only consider non-empty values
            asset_id = asset.get("assetId")
            if asset_id is not None:  # Ensure assetId exists
                groups[value].append({
                    "asset_id": asset_id,
                    "asset": asset
                })
    
    new_duplicates = []
    for value, group in groups.items():
        if len(group) > 1:
            # Check if this group has any new pairs not flagged
            group_ids = [item["asset_id"] for item in group]
            group_pairs = [frozenset([id1, id2]) for id1, id2 in combinations(group_ids, 2)]
            if all(pair not in flagged_pairs for pair in group_pairs):
                new_duplicates.append((value, group))
                # Flag all pairs in this group
                for pair in group_pairs:
                    flagged_pairs.add(pair)
    
    num_duplicates = len(new_duplicates)
    if field_name == "assetName":
        print(f"--------------------------------------------------------------------")
        print(f"\n{num_duplicates} Potential duplicates based on {display_name}")
    else:
        print(f"--------------------------------------------------------------------")
        print(f"\n{num_duplicates} Potential duplicates based on {display_name}, not reported previously\n")
    
    if num_duplicates > 0:
        for value, group in new_duplicates:
            print(f"\n- {display_name}: '{value}'")
            for item in group:
                print(f"  * Asset ID: {item['asset_id']}")

# Optionally save to JSON file
with open("all_assets.json", "w") as f:
    json.dump(all_assets, f, indent=2)

print("\nAll fetched assets saved to all_assets.json\n")

# Logout / Invalidate token by posting with token=false
logout_data = {
    "username": username,
    "password": password,
    "token": "false"
}
logout_response = requests.post(auth_url, headers=auth_headers, data=logout_data)
if logout_response.status_code == 200 or logout_response.status_code == 201:
    print("Logout successful.")
else:
    print("Logout may have failed, but token will expire in 4 hours.")
    print(logout_response.text)
