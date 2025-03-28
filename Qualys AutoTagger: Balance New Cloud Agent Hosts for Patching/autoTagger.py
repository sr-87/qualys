import requests
import base64
import xml.etree.ElementTree as ET
from getpass import getpass
from datetime import datetime, timedelta

# Platform selection
print("Options: US1, US2, US3, US4, UK, EU1, EU2, EU3, IN, CA, AE, AU, KSA")
platform = input("What platform is your account on? ").upper()

# Define base URLs for each platform
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
    exit(1)

# Input credentials
username = input("Enter your username: ")
password = getpass("Enter your password: ")

# Define authentication URLs
auth_url = f"{base_url}/api/2.0/fo/session/"
logout_url = f"{base_url}/api/2.0/fo/session/"

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
    exit(1)

# Logout operation
logout_headers = {
    "X-Requested-With": "Curl Sample",
}
logout_data = {
    "action": "logout"
}
logout_response = requests.post(logout_url, headers=logout_headers, data=logout_data, cookies=auth_response.cookies)

# Encode credentials to Base64
credentials = f'{username}:{password}'
auth_token = base64.b64encode(credentials.encode('utf-8')).decode('utf-8')

# Define headers for API requests
headers = {
    'Content-Type': 'text/xml',
    'X-Requested-With': 'Python Script',
    'Authorization': f'Basic {auth_token}',
    'Cache-Control': 'no-cache'
}

def check_uat_tags():
    """Check if UAT tags exist, are static, and store their IDs"""
    tag_search_url = f"{base_url}/qps/rest/2.0/search/am/tag/"
    uat_tags = ["UATMonday", "UATTuesday", "UATWednesday", "UATThursday"]
    existing_tags = []
    dynamic_tags = []
    tag_ids = {}
    
    for tag in uat_tags:
        xml_payload = f"""<?xml version="1.0" encoding="UTF-8"?>
        <ServiceRequest>
            <filters>
                <Criteria field="name" operator="EQUALS">{tag}</Criteria>
            </filters>
        </ServiceRequest>"""

        try:
            response = requests.post(tag_search_url, headers=headers, data=xml_payload)
            if response.status_code == 200:
                root = ET.fromstring(response.text)
                response_code = root.find('responseCode')
                
                if response_code is not None and response_code.text == "SUCCESS":
                    tag_elements = root.findall(".//Tag")
                    if tag_elements:
                        for tag_elem in tag_elements:
                            is_dynamic = tag_elem.find("ruleType") is not None
                            tag_name = tag_elem.find("name").text
                            tag_id = tag_elem.find("id").text
                            if tag_name == tag:
                                existing_tags.append(tag)
                                tag_ids[tag] = tag_id
                                if is_dynamic:
                                    dynamic_tags.append(tag)
                else:
                    print(f"Error checking tag {tag}:")
            else:
                print(f"Tag search for {tag} failed with status code: {response.status_code}")
        except requests.exceptions.RequestException as e:
            print(f"Error making API request for tag {tag}: {e}")
        except ET.ParseError as e:
            print(f"Error parsing XML response for tag {tag}: {e}")

    missing_tags = [tag for tag in uat_tags if tag not in existing_tags]
    return existing_tags, missing_tags, dynamic_tags, tag_ids

def get_recent_agents(days_back=7):
    """Retrieve agent hosts created in the last specified number of days and check UAT tags"""
    search_url = f"{base_url}/qps/rest/2.0/search/am/hostasset/"
    date_threshold = datetime.now() - timedelta(days=days_back)
    date_str = date_threshold.strftime("%Y-%m-%dT%H:%M:%SZ")

    xml_payload = f"""<?xml version="1.0" encoding="UTF-8"?>
    <ServiceRequest>
        <filters>
            <Criteria field="tagName" operator="EQUALS">Testing</Criteria>
            <Criteria field="created" operator="GREATER">{date_str}</Criteria>
        </filters>
    </ServiceRequest>"""

    try:
        response = requests.post(search_url, headers=headers, data=xml_payload)
        if response.status_code == 200:
            root = ET.fromstring(response.text)
            response_code = root.find('responseCode')
            
            if response_code is not None and response_code.text == "SUCCESS":
                all_hosts = []
                hosts_without_uat = []
                uat_tags = {"UATMonday", "UATTuesday", "UATWednesday", "UATThursday"}
                
                for host in root.findall(".//HostAsset"):
                    host_id = host.find("id").text if host.find("id") is not None else "N/A"
                    host_name = host.find("name").text if host.find("name") is not None else "N/A"
                    created_date = host.find("created").text if host.find("created") is not None else "N/A"
                    
                    tags = host.findall(".//TagSimple/name")
                    tag_names = [tag.text for tag in tags if tag.text is not None]
                    
                    host_data = {
                        "id": host_id,
                        "name": host_name,
                        "created": created_date,
                        "tags": tag_names
                    }
                    all_hosts.append(host_data)
                    
                    has_uat_tag = any(tag in uat_tags for tag in tag_names)
                    if not has_uat_tag:
                        hosts_without_uat.append(host_data)
                
                return all_hosts, hosts_without_uat
            else:
                print("Error: API request failed")
                return None, None
        else:
            print(f"API request failed with status code: {response.status_code}")
            return None, None
    except requests.exceptions.RequestException as e:
        print(f"Error making API request: {e}")
        return None, None
    except ET.ParseError as e:
        print(f"Error parsing XML response: {e}")
        return None, None

def count_assets_by_uat_tag():
    """Count assets associated with each UAT tag"""
    count_url = f"{base_url}/qps/rest/2.0/count/am/hostasset"
    uat_tags = ["UATMonday", "UATTuesday", "UATWednesday", "UATThursday"]
    tag_counts = {}
    
    for tag in uat_tags:
        xml_payload = f"""<?xml version="1.0" encoding="UTF-8"?>
        <ServiceRequest>
            <filters>
                <Criteria field="tagName" operator="EQUALS">{tag}</Criteria>
            </filters>
        </ServiceRequest>"""

        try:
            response = requests.post(count_url, headers=headers, data=xml_payload)
            if response.status_code == 200:
                root = ET.fromstring(response.text)
                response_code = root.find('responseCode')
                
                if response_code is not None and response_code.text == "SUCCESS":
                    count_elem = root.find('count')
                    count = int(count_elem.text) if count_elem is not None else 0
                    tag_counts[tag] = count
                    print(f"Count for {tag}: {count}")
                else:
                    print(f"Error counting assets for {tag}:")
                    print(f"Response: {response.text}")
                    tag_counts[tag] = None
            else:
                print(f"Failed to count assets for {tag} with status code: {response.status_code}")
                print(f"Response: {response.text}")
                tag_counts[tag] = None
        except requests.exceptions.RequestException as e:
            print(f"Error making API request for {tag}: {e}")
            tag_counts[tag] = None
        except ET.ParseError as e:
            print(f"Error parsing XML response for {tag}: {e}")
            tag_counts[tag] = None
    
    return tag_counts

def assign_tags_to_assets(hosts, tag_counts, tag_ids):
    """Assign hosts to UAT tags to balance counts evenly"""
    update_url = f"{base_url}/qps/rest/2.0/update/am/asset"
    uat_tags = ["UATMonday", "UATTuesday", "UATWednesday", "UATThursday"]
    
    # Validate inputs
    valid_counts = {tag: count for tag, count in tag_counts.items() if count is not None}
    if not valid_counts or len(valid_counts) != len(uat_tags):
        print("Not all tags have valid counts. Skipping assignment.")
        return tag_counts
    
    # Calculate total and target distribution
    total_existing = sum(valid_counts.values())
    total_new = len(hosts)
    total_assets = total_existing + total_new
    base_count = total_assets // len(uat_tags)
    extra = total_assets % len(uat_tags)
    print(f"\nAssigning {total_new} new assets to balance across all tags (target: {base_count} or {base_count + 1})")
    
    # Pre-calculate target counts
    target_counts = {}
    for i, tag in enumerate(uat_tags):
        target_counts[tag] = base_count + (1 if i < extra else 0)
    
    # Track updated counts and assignments
    updated_counts = tag_counts.copy()
    assignments = {tag: [] for tag in uat_tags}
    
    # Distribute hosts
    for host in hosts:
        # Find tag furthest below its target
        target_tag = min(uat_tags, key=lambda tag: updated_counts[tag] - target_counts[tag])
        tag_id = tag_ids.get(target_tag)
        if not tag_id:
            print(f"Tag ID for {target_tag} not found. Skipping host {host['id']}.")
            continue
        
        xml_payload = f"""<?xml version="1.0" encoding="UTF-8"?>
        <ServiceRequest>
            <filters>
                <Criteria field="id" operator="IN">{host['id']}</Criteria>
            </filters>
            <data>
                <Asset>
                    <tags>
                        <add>
                            <TagSimple><id>{tag_id}</id></TagSimple>
                        </add>
                    </tags>
                </Asset>
            </data>
        </ServiceRequest>"""
        
        try:
            response = requests.post(update_url, headers=headers, data=xml_payload)
            if response.status_code == 200:
                root = ET.fromstring(response.text)
                response_code = root.find('responseCode')
                if response_code is not None and response_code.text == "SUCCESS":
                    print(f"Successfully assigned {target_tag} (ID: {tag_id}) to host {host['id']} ({host['name']})")
                    updated_counts[target_tag] += 1
                    assignments[target_tag].append(host)
                else:
                    print(f"Failed to assign {target_tag} to host {host['id']}:")
                    print(f"Response: {response.text}")
            else:
                print(f"Failed to assign {target_tag} to host {host['id']} with status code: {response.status_code}")
                print(f"Response: {response.text}")
        except requests.exceptions.RequestException as e:
            print(f"Error making API request for host {host['id']}: {e}")
    
    # Print updated counts
    print("\nUpdated counts after assignment:")
    for tag, count in updated_counts.items():
        print(f"Count for {tag}: {count if count is not None else 'N/A'}")
    
    return updated_counts

def print_host_details(hosts, message):
    """Print host details with attributes on separate lines and spacing between hosts"""
    print(f"{message} {len(hosts)} hosts:")
    for i, host in enumerate(hosts):
        print(f"ID: {host['id']}")
        print(f"Name: {host['name']}")
        print(f"Created: {host['created']}")
        print(f"Tags: {', '.join(host['tags'])}")
        if i < len(hosts) - 1:
            print("\n\n")

def main():
    # Step 1: Check UAT tags and get their IDs
    print("\nStep 1: Checking for UAT tags and their type...")
    existing_tags, missing_tags, dynamic_tags, tag_ids = check_uat_tags()
    
    if existing_tags:
        print("\nExisting UAT tags:")
        for tag in existing_tags:
            print(f"- {tag}")
    else:
        print("\nNo existing UAT tags found")
    
    if missing_tags:
        print("\nMissing UAT tags:")
        for tag in missing_tags:
            print(f"- {tag}")
    
    if dynamic_tags:
        print("\nDynamic (non-static) UAT tags:")
        for tag in dynamic_tags:
            print(f"- {tag}")
        print("\nOne or more required tags are present but dynamic (have ruleType). All tags must be static to proceed. Exiting.")
        exit(1)
    
    if missing_tags:
        print("\nNot all required UAT tags (UATMonday, UATTuesday, UATWednesday, UATThursday) were found. Exiting.")
        exit(1)
    else:
        print("\nAll required UAT tags are present and static")

    # Step 2: Get recent hosts
    print("\nStep 2: Checking for recently created agent hosts...")
    all_hosts, hosts_without_uat = get_recent_agents(days_back=7)
    
    if all_hosts is None or len(all_hosts) == 0:
        print("No recent hosts found. Exiting.")
        exit(0)
    
    print_host_details(all_hosts, "Found")

    # Step 3: Filter hosts without UAT tags
    print("\nStep 3: Checking hosts for UAT tags...")
    if hosts_without_uat:
        print_host_details(hosts_without_uat, "Found hosts without any UAT tags (proceeding to next step):")
    else:
        print("All recent hosts already have UAT tags applied. No further action needed.")
        return

    # Step 4: Count assets and assign tags
    print("\nStep 4: Counting assets and assigning tags...")
    tag_counts = count_assets_by_uat_tag()
    if hosts_without_uat:
        assign_tags_to_assets(hosts_without_uat, tag_counts, tag_ids)

if __name__ == "__main__":
    main()
