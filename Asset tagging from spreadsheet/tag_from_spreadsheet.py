import requests
import base64
import xml.etree.ElementTree as ET
from getpass import getpass
import pandas as pd

#Ask for the platform selection
print("\nOptions: US1, US2, US3, US4, UK, EU1, EU2, EU3, IN, CA, AE, AU, KSA\n")
platform = input("What platform is your account on? ").upper()

#Define base URLs for each platform
base_urls = {
    "US1": "https://qualysapi.qualys.com",
    "US2": "https://qualysapi.qg2.apps.qualys.com",
    "US3": "https://qualysapi.qg3.apps.qualys.com",
    "US4": "https://qualysapi.qg4.apps.qualys.com",
    "UK": "https://qualysapi.qg1.apps.qualys.co.uk",
    "EU1": "https://qualysapi.qualys.eu",
    "EU2": "https://qualysapi.qg2.apps.qualys.eu",
    "EU3": "https://qualysapi.qg3.apps.qualys.it",
    "IN": "https://qualysapi.qg1.apps.qualys.in",
    "CA": "https://qualysapi.qg1.apps.qualys.ca",
    "AE": "https://qualysapi.qg1.apps.qualys.ae",
    "AU": "https://qualysapi.qg1.apps.qualys.com.au",
    "KSA": "https://qualysapi.qg1.apps.qualysksa.com"
}

# Select the correct base URL
if platform in base_urls:
    base_url = base_urls[platform]
else:
    print("Invalid platform selection. Exiting")
    exit(1)  # Exit if platform detail is incorrect

# Define the authentication URL using the base URL
auth_url = f"{base_url}/api/2.0/fo/session/"

# Input for username and password at runtime
username = input("Enter your username: ")
password = getpass("Enter your password: ")

# Authentication headers and data
auth_headers = {
    "X-Requested-With": "Python Script"
}
auth_data = {
    "action": "login",
    "username": username,
    "password": password
}

# Perform authentication to check credentials
auth_response = requests.post(auth_url, headers=auth_headers, data=auth_data)

if auth_response.status_code != 200:
    print("Authentication failed.")
    print(auth_response.text)
    exit(1)  # Exit the script if authentication fails

# Encode the credentials to Base64 for Basic Auth
credentials = f'{username}:{password}'
auth_token = base64.b64encode(credentials.encode('utf-8')).decode('utf-8')

# Read the spreadsheet
try:
    df = pd.read_excel("Assets_needing_tags.xlsx", header=None)  # No headers assumed
    # Assuming data starts from row 1; adjust if there's a header row: df = pd.read_excel(..., header=None, skiprows=1)
except FileNotFoundError:
    print("\nFile not found. Please check the file name and path.")
    exit(1)
except Exception as e:
    print(f"Error reading the spreadsheet: {e}")
    exit(1)

# Cache for tag names to IDs (or None if not found)
tag_cache = {}

# Process each row
for index, row in df.iterrows():
    asset_name = row[0]  # Column A
    if pd.isna(asset_name):
        continue  # Skip empty rows
    desired_tags_str = row[1] if not pd.isna(row[1]) else ""  # Column B
    desired_tags = [tag.strip() for tag in desired_tags_str.split(',') if tag.strip()]  # Split by comma, strip whitespace

    # Step 1: Search for the asset
    search_asset_url = f"{base_url}/qps/rest/2.0/search/am/asset"
    headers = {
        "Content-Type": "text/xml",
        "X-Requested-With": "Python Script",
        "Authorization": f"Basic {auth_token}"
    }
    xml_asset_payload = f"""
    <ServiceRequest>
        <filters>
            <Criteria field="name" operator="EQUALS">{asset_name}</Criteria>
        </filters>
    </ServiceRequest>
    """
    asset_response = requests.post(search_asset_url, headers=headers, data=xml_asset_payload)
    
    if asset_response.status_code != 200 or '<responseCode>SUCCESS</responseCode>' not in asset_response.text:
        print(f"\nError searching asset '{asset_name}': {asset_response.text}")
        continue
    
    # Parse asset response XML
    root = ET.fromstring(asset_response.text)
    assets = root.findall(".//Asset")
    if not assets:
        print(f"\nNo asset found for '{asset_name}'")
        continue
    # Assume first match (handle multiples if needed)
    asset = assets[0]
    asset_id = asset.find('id').text
    existing_tags = {}
    for tag_simple in asset.findall(".//TagSimple"):
        tag_id = tag_simple.find('id').text
        tag_name = tag_simple.find('name').text
        existing_tags[tag_id] = tag_name  # Dict of id: name for easy lookup
    
    # Step 2: For each desired tag, search for its ID (using cache)
    new_tag_ids = []
    new_tag_names = []  # Collect names here for output
    tags_not_applied = []
    for desired_tag_name in desired_tags:
        if desired_tag_name in tag_cache:
            if tag_cache[desired_tag_name] is None:
                tags_not_applied.append(desired_tag_name)
                continue
            else:
                tag_id = tag_cache[desired_tag_name]
        else:
            search_tag_url = f"{base_url}/qps/rest/2.0/search/am/tag"
            xml_tag_payload = f"""
            <ServiceRequest>
                <filters>
                    <Criteria field="name" operator="EQUALS">{desired_tag_name}</Criteria>
                </filters>
            </ServiceRequest>
            """
            tag_response = requests.post(search_tag_url, headers=headers, data=xml_tag_payload)
            
            if tag_response.status_code != 200 or '<responseCode>SUCCESS</responseCode>' not in tag_response.text:
                print(f"\nError searching tag '{desired_tag_name}' for asset '{asset_name}': {tag_response.text}")
                continue
            
            # Parse tag response
            tag_root = ET.fromstring(tag_response.text)
            tags = tag_root.findall(".//Tag")
            if not tags:
                print(f"\nNo tag found for '{desired_tag_name}' - skipping")
                tag_cache[desired_tag_name] = None
                tags_not_applied.append(desired_tag_name)
                continue
            else:
                # Assume first match
                tag = tags[0]
                tag_id = tag.find('id').text
                tag_cache[desired_tag_name] = tag_id
        
        # Check if already applied (by ID)
        if tag_id not in existing_tags:
            new_tag_ids.append(tag_id)
            new_tag_names.append(desired_tag_name)

    # Step 3: If new tags, update the asset
    if new_tag_ids:
        update_url = f"{base_url}/qps/rest/2.0/update/am/asset"
        add_tags_xml = "".join([f"<TagSimple><id>{tid}</id></TagSimple>" for tid in new_tag_ids])
        xml_update_payload = f"""
        <ServiceRequest>
            <filters>
                <Criteria field="id" operator="EQUALS">{asset_id}</Criteria>
            </filters>
            <data>
                <Asset>
                    <tags>
                        <add>
                            {add_tags_xml}
                        </add>
                    </tags>
                </Asset>
            </data>
        </ServiceRequest>
        """
        update_response = requests.post(update_url, headers=headers, data=xml_update_payload)
        
        if update_response.status_code == 200 and '<responseCode>SUCCESS</responseCode>' in update_response.text:
            print(f"\nUpdated asset '{asset_name}' with new tags")
        else:
            print(f"\nError updating asset '{asset_name}': {update_response.text}")
            # If update fails, consider them not applied
            tags_not_applied.extend(new_tag_names)
            new_tag_names = []  # Reset applied
    
    # Step 4: Print output in new format
    print(f"\nAsset name: {asset_name}")
    print(f"New tags applied: {', '.join(new_tag_names) if new_tag_names else 'None'}")
    print(f"Tags not applied: {', '.join(tags_not_applied) if tags_not_applied else 'None'}")
    print()  # Blank line for separation

# Logout operation to end the session
logout_headers = {
    "X-Requested-With": "Curl Sample",
}
logout_data = {
    "action": "logout"
}
logout_url = f"{base_url}/api/2.0/fo/session/"

# Perform logout using the session cookies from the authentication request
logout_response = requests.post(logout_url, headers=logout_headers, data=logout_data, cookies=auth_response.cookies)
#print("\nLogout Response:")
#print(logout_response.text)