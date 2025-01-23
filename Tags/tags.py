import requests
import base64
import xml.etree.ElementTree as ET
from getpass import getpass

# Ask for the platform selection
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

# Logout operation
logout_headers = {
    "X-Requested-With": "Curl Sample",
}
logout_data = {
    "action": "logout"
}
logout_url = f"{base_url}/api/2.0/fo/session/"

# Perform logout using the session cookies from the authentication request
logout_response = requests.post(logout_url, headers=logout_headers, data=logout_data, cookies=auth_response.cookies)

# Define the tag URL using the base URL
tag_url = f"{base_url}/qps/rest/2.0/create/am/tag"

# Define the XML payload for creating the "OS: Operating Systems" parent tag
xml_payload_for_parent_OS = """
<ServiceRequest>
    <data>
        <Tag>
            <name>OS: Operating Systems</name>
            <ruleType>STATIC</ruleType>
        </Tag>
    </data>
</ServiceRequest>
"""

# Set headers
headers = {
    "Content-type": "text/xml"
}

# Send the POST request to create the parent tag
response = requests.post(tag_url, auth=(username, password), headers=headers, data=xml_payload_for_parent_OS)

# Parse the XML response to check if the tag was created successfully
root = ET.fromstring(response.text)
response_code = root.find('responseCode')

if response_code is not None and response_code.text == "SUCCESS":
    print('\n\nCreated parent tag "OS: Operating Systems"')
    
    # Parse the XML response and extract the <id> element value
    root = ET.fromstring(response.text)
    id_element = root.find(".//id")
    if id_element is not None:
        tag_id = id_element.text
        
        # XML payloads for child tags under "OS: Operating Systems"
        child_tags = [
            ("OS: Windows Server", """<ServiceRequest>
                <data>
                    <Tag>
                        <name>OS: Windows Server</name>
                        <parentTagId>{tag_id}</parentTagId>
                        <ruleText>operatingSystem.category1:`Windows` and operatingSystem.category2:`Server`</ruleText>
                        <ruleType>GLOBAL_ASSET_VIEW</ruleType>
                        <criticalityScore>4</criticalityScore>
                    </Tag>
                </data>
            </ServiceRequest>"""),
            
            ("OS: Windows Client", """<ServiceRequest>
                <data>
                    <Tag>
                        <name>OS: Windows Client</name>
                        <parentTagId>{tag_id}</parentTagId>
                        <ruleText>operatingSystem.category1:`Windows` and operatingSystem.category2:`Client`</ruleText>
                        <ruleType>GLOBAL_ASSET_VIEW</ruleType>
                        <criticalityScore>2</criticalityScore>
                    </Tag>
                </data>
            </ServiceRequest>"""),
            
            ("OS: Linux Server", """<ServiceRequest>
                <data>
                    <Tag>
                        <name>OS: Linux Server</name>
                        <parentTagId>{tag_id}</parentTagId>
                        <ruleText>operatingSystem.category1:`Linux` and operatingSystem.category2:`Server`</ruleText>
                        <ruleType>GLOBAL_ASSET_VIEW</ruleType>
                        <criticalityScore>4</criticalityScore>
                    </Tag>
                </data>
            </ServiceRequest>"""),
            
            ("OS: Linux Client", """<ServiceRequest>
                <data>
                    <Tag>
                        <name>OS: Linux Client</name>
                        <parentTagId>{tag_id}</parentTagId>
                        <ruleText>operatingSystem.category1:`Linux` and operatingSystem.category2:`Client`</ruleText>
                        <ruleType>GLOBAL_ASSET_VIEW</ruleType>
                        <criticalityScore>2</criticalityScore>
                    </Tag>
                </data>
            </ServiceRequest>"""),
            
            ("OS: Network OS", """<ServiceRequest>
                <data>
                    <Tag>
                        <name>OS: Network OS</name>
                        <parentTagId>{tag_id}</parentTagId>
                        <ruleText>operatingSystem.category1:`Network Operating System`</ruleText>
                        <ruleType>GLOBAL_ASSET_VIEW</ruleType>
                        <criticalityScore>3</criticalityScore>
                    </Tag>
                </data>
            </ServiceRequest>""")
        ]

        # Create each child tag separately
        for tag_name, payload in child_tags:
            child_response = requests.post(tag_url, auth=(username, password), headers=headers, data=payload.format(tag_id=tag_id))
            root_child = ET.fromstring(child_response.text)
            response_code_child = root_child.find('responseCode')
            
            if response_code_child is not None and response_code_child.text == "SUCCESS":
                print(f"Created child tag: {tag_name}")
            else:
                print(f"Tag {tag_name} not created.")
                print(f"Response:\n{child_response.text}")
    else:
        print("Tag ID not found in the response.")
else:
    print('Failed to create parent tag "OS: Operating Systems"')
    print('\n\nHere is the XML response\n\n')
    print(response.text)

# Define the XML payload for creating the "Type: Asset Types" parent tag
xml_payload_for_parent_Asset_Types = """
<ServiceRequest>
    <data>
        <Tag>
            <name>Type: Asset Types</name>
            <ruleType>STATIC</ruleType>
        </Tag>
    </data>
</ServiceRequest>
"""

# Send the POST request to create the parent tag for Asset Types
response_asset_types = requests.post(tag_url, auth=(username, password), headers=headers, data=xml_payload_for_parent_Asset_Types)

# Parse the XML response to check if the tag was created successfully
root_asset_types = ET.fromstring(response_asset_types.text)
response_code_asset_types = root_asset_types.find('responseCode')

if response_code_asset_types is not None and response_code_asset_types.text == "SUCCESS":
    print('\n\nCreated parent tag "Type: Asset Types"')
    
    # Parse the XML response and extract the <id> element value for the new parent
    id_element_asset_types = root_asset_types.find(".//id")
    if id_element_asset_types is not None:
        tag_id_2 = id_element_asset_types.text
            
        # XML payloads for child tags under "Type: Asset Types"
        asset_type_payloads = [
            ("Type: Domain Controllers", """<ServiceRequest>
                <data>
                    <Tag>
                        <name>Type: Domain Controllers</name>
                        <parentTagId>{tag_id_2}</parentTagId>
                        <ruleText>asset.domainRole:`Primary Domain Controller`</ruleText>
                        <ruleType>GLOBAL_ASSET_VIEW</ruleType>
                        <criticalityScore>5</criticalityScore>
                    </Tag>
                </data>
            </ServiceRequest>"""),
            
            ("Type: Network Devices", """<ServiceRequest>
                <data>
                    <Tag>
                        <name>Type: Network Devices</name>
                        <parentTagId>{tag_id_2}</parentTagId>
                        <ruleText>hardware.category1:Networking Device or hardware.category1:Network Security Device</ruleText>
                        <ruleType>GLOBAL_ASSET_VIEW</ruleType>
                        <criticalityScore>3</criticalityScore>
                    </Tag>
                </data>
            </ServiceRequest>"""),
            
            ("Type: Printers", """<ServiceRequest>
                <data>
                    <Tag>
                        <name>Type: Printers</name>
                        <parentTagId>{tag_id_2}</parentTagId>
                        <ruleText>hardware.category1:Printers</ruleText>
                        <ruleType>GLOBAL_ASSET_VIEW</ruleType>
                        <criticalityScore>1</criticalityScore>
                    </Tag>
                </data>
            </ServiceRequest>"""),
            
            ("Type: Database Servers", """<ServiceRequest>
                <data>
                    <Tag>
                        <name>Type: Database Servers</name>
                        <parentTagId>{tag_id_2}</parentTagId>
                        <ruleText>software:(category1:Databases and component:Server) and ((hardware.category2:`Server` or operatingSystem.category2:`Server`))</ruleText>
                        <ruleType>GLOBAL_ASSET_VIEW</ruleType>
                        <criticalityScore>4</criticalityScore>
                    </Tag>
                </data>
            </ServiceRequest>"""),
            
            ("Type: Clients/Workstations", """<ServiceRequest>
                <data>
                    <Tag>
                        <name>Type: Clients/Workstations</name>
                        <parentTagId>{tag_id_2}</parentTagId>
                        <ruleText>operatingSystem.category2:`Client` or hardware.category2:Desktop</ruleText>
                        <ruleType>GLOBAL_ASSET_VIEW</ruleType>
                        <criticalityScore>2</criticalityScore>
                    </Tag>
                </data>
            </ServiceRequest>"""),
            
            ("Type: Servers", """<ServiceRequest>
                <data>
                    <Tag>
                        <name>Type: Servers</name>
                        <parentTagId>{tag_id_2}</parentTagId>
                        <ruleText>operatingSystem.category2:`Server` or hardware.category2:Server</ruleText>
                        <ruleType>GLOBAL_ASSET_VIEW</ruleType>
                        <criticalityScore>4</criticalityScore>
                    </Tag>
                </data>
            </ServiceRequest>""")
        ]

        # Create each child tag separately
        for tag_name, payload in asset_type_payloads:
            child_response = requests.post(tag_url, auth=(username, password), headers=headers, data=payload.format(tag_id_2=tag_id_2))
            root_child = ET.fromstring(child_response.text)
            response_code_child = root_child.find('responseCode')
            
            if response_code_child is not None and response_code_child.text == "SUCCESS":
                print(f"Created child tag: {tag_name}")
            else:
                print(f"Tag {tag_name} not created.")
                print(f"Response:\n{child_response.text}")
    else:
        print("Tag ID not found in the response.")
else:
    print('Failed to create parent tag "Type: Asset Types"')
    print('\n\nHere is the XML response\n\n')
    print(response_asset_types.text)
