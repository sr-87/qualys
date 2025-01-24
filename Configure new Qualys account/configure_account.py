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

# Encode the credentials to Base64
credentials = f'{username}:{password}'
auth_token = base64.b64encode(credentials.encode('utf-8')).decode('utf-8')


##################### Create asset tags #####################

# Define the tag URL
tag_url = f"{base_url}/qps/rest/2.0/create/am/tag"

# Set headers
headers = {
    "Content-type": "text/xml"
}

# Function to create parent tag
def create_parent_tag(tag_name):
    xml_payload = f"""
    <ServiceRequest>
        <data>
            <Tag>
                <name>{tag_name}</name>
                <ruleType>STATIC</ruleType>
            </Tag>
        </data>
    </ServiceRequest>
    """
    response = requests.post(tag_url, auth=(username, password), headers=headers, data=xml_payload)
    root = ET.fromstring(response.text)
    response_code = root.find('responseCode')
    if response_code is not None and response_code.text == "SUCCESS":
        print(f'\nCreated parent tag "{tag_name}"')
        id_element = root.find(".//id")
        if id_element is not None:
            return id_element.text
    else:
        print(f'\nError: Failed to create parent tag "{tag_name}"\n')
        print("\n########################## Start of Output ##########################\n")
        print(f'Response:\n{response.text}')
        print("\n########################## End of Output ##########################\n\n")
    return None

# Function to create child tags
def create_child_tags(child_tags, parent_tag_id):
    for tag_name, payload in child_tags:
        child_response = requests.post(tag_url, auth=(username, password), headers=headers, data=payload.format(tag_id=parent_tag_id))
        root_child = ET.fromstring(child_response.text)
        response_code_child = root_child.find('responseCode')
        if response_code_child is not None and response_code_child.text == "SUCCESS":
            print(f"Created child tag: {tag_name}")
        else:
            print(f"Tag {tag_name} not created.")
            print(f"Response:\n{child_response.text}")

# Create "OS: Operating Systems" parent tag and its children
os_parent_id = create_parent_tag("OS: Operating Systems")
if os_parent_id:
    os_child_tags = [
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
        </ServiceRequest>"""),

        ("OS: MacOS", """<ServiceRequest>
            <data>
                <Tag>
                    <name>OS: MacOS</name>
                    <parentTagId>{tag_id}</parentTagId>
                    <ruleText>operatingSystem.category1:`MacOS`</ruleText>
                    <ruleType>GLOBAL_ASSET_VIEW</ruleType>
                    <criticalityScore>2</criticalityScore>
                </Tag>
            </data>
        </ServiceRequest>""")
    ]
    create_child_tags(os_child_tags, os_parent_id)

# Create "Type: Asset Types" parent tag and its children
asset_type_parent_id = create_parent_tag("Type: Asset Types")
if asset_type_parent_id:
    asset_type_child_tags = [
        ("Type: Domain Controllers", """<ServiceRequest>
            <data>
                <Tag>
                    <name>Type: Domain Controllers</name>
                    <parentTagId>{tag_id}</parentTagId>
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
                    <parentTagId>{tag_id}</parentTagId>
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
                    <parentTagId>{tag_id}</parentTagId>
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
                    <parentTagId>{tag_id}</parentTagId>
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
                    <parentTagId>{tag_id}</parentTagId>
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
                    <parentTagId>{tag_id}</parentTagId>
                    <ruleText>operatingSystem.category2:`Server` or hardware.category2:Server</ruleText>
                    <ruleType>GLOBAL_ASSET_VIEW</ruleType>
                    <criticalityScore>4</criticalityScore>
                </Tag>
            </data>
        </ServiceRequest>""")
    ]
    create_child_tags(asset_type_child_tags, asset_type_parent_id)

##################### Create activation key #####################

# Define the headers for creating activation key
headers_act_key = {
    'Content-Type': 'text/xml',
    'X-Requested-With': 'curl',
    'Authorization': f'Basic {auth_token}',
    'Cxml': '',
    'CacheControl': 'no-cache',
}

# Define the XML data for creating activation key
xml_data_act_key = '''
<ServiceRequest>
  <data>
    <AgentActKey>
      <title>Default Key</title>    
      <countPurchased>0</countPurchased>
      <type>UNLIMITED</type>
      <modules>
        <list>
          <ActivationKeyModule>
            <license>PM</license>
          </ActivationKeyModule>
          <ActivationKeyModule>
            <license>VM_LICENSE</license>
          </ActivationKeyModule>
          <ActivationKeyModule>
            <license>SCA</license>
          </ActivationKeyModule>
        </list>
      </modules>
    </AgentActKey>
  </data>
</ServiceRequest>
'''

# Define the URL for creating activation key
act_key_url = f"{base_url}/qps/rest/1.0/create/ca/agentactkey/"

# Make the POST request
response_act_key = requests.post(act_key_url, headers=headers_act_key, data=xml_data_act_key)

# Check if the request was successful
if response_act_key.status_code == 200:
    if '<responseCode>SUCCESS</responseCode>' in response_act_key.text:
        print("\n\nNew activation key created")
    else:
        print("\n\nError: Failed to create new activation key")
        print("\n########################## Start of Output ##########################\n")
        print(f"{response_act_key.text}")
        print("\n########################## End of Output ##########################\n\n")

##################### Create and update agent config #####################

# Define the XML data for creating agent config
xml_data_create = '''
<ServiceRequest>
  <data>
    <AgentConfig>
      <name>Default</name>
      <isDefault>1</isDefault>
      <inMemoryDbEnabled>true</inMemoryDbEnabled>
      <tags>
        <includeTags></includeTags>
        <includeResolution>ANY</includeResolution>
        <excludeTags></excludeTags>
        <excludeResolution>ANY</excludeResolution>
      </tags>
      <blackoutConfig/>
      <performanceProfile>
        <settings>
          <list>
            <PerformanceLevelSettings>
              <key>CPU_LIMIT</key>
              <value>10</value>
            </PerformanceLevelSettings>
            <PerformanceLevelSettings>
              <key>INTERVAL_EVENT_UPLOAD_CHANGELIST</key>
              <value>5</value>
            </PerformanceLevelSettings>
            <PerformanceLevelSettings>
              <key>FILE_UPLOAD_FRAGMENT_SIZE_IN_KB</key>
              <value>4096</value>
            </PerformanceLevelSettings>
            <PerformanceLevelSettings>
              <key>AGENT_LOGGING_LEVEL</key>
              <value>0</value>
            </PerformanceLevelSettings>
            <PerformanceLevelSettings>
              <key>THROTTLE_EVENT_COMM_DOWNLOAD</key>
              <value>0</value>
            </PerformanceLevelSettings>
            <PerformanceLevelSettings>
              <key>THROTTLE_EVENT_SCAN</key>
              <value>5</value>
            </PerformanceLevelSettings>
            <PerformanceLevelSettings>
              <key>PRIORITY_STATUS_UPLOAD_INTERVAL</key>
              <value>300</value>
            </PerformanceLevelSettings>
            <PerformanceLevelSettings>
              <key>INTERVAL_EVENT_EXECUTE_SETUP</key>
              <value>32400</value>
            </PerformanceLevelSettings>
            <PerformanceLevelSettings>
              <key>THROTTLE_EVENT_COMM_UPLOAD</key>
              <value>0</value>
            </PerformanceLevelSettings>
            <PerformanceLevelSettings>
              <key>INTERVAL_EVENT_STATUS</key>
              <value>900</value>
            </PerformanceLevelSettings>
          </list>
        </settings>
      </performanceProfile>
    </AgentConfig>
  </data>
</ServiceRequest>
'''

# Define the URL for creating agent config
url_create = f"{base_url}/qps/rest/1.0/create/ca/agentconfig/"

# Make the POST request for creating agent config
response_create = requests.post(url_create, headers=headers_act_key, data=xml_data_create)

# Check if the request was successful
if response_create.status_code == 200:
    # Parse the XML response
    root = ET.fromstring(response_create.text)

    # Find the config profile named "Default" and extract its ID
    default_config_id = None
    for agent_config in root.findall('.//AgentConfig'):
        name = agent_config.find('name').text
        if name == 'Default':
            default_config_id = agent_config.find('id').text
            break

    if default_config_id is None:
        print("Error: Failed to create new configuration profile")
        print("\n########################## Start of Output ##########################\n")
        print(f"{response_create.text}")
        print("\n########################## End of Output ##########################\n\n")
    else:
        print("\nNew configuration profile created")

        # Define the URL for updating agent config
        url_update = f"{base_url}/qps/rest/1.0/update/ca/agentconfig/"

        # Construct the XML data for updating agent config
        xml_data_update = f'''
        <ServiceRequest>
          <data>
            <AgentConfig>
              <id>{default_config_id}</id>
              <name>Default</name>
              <isDefault>1</isDefault>
              <priority>1</priority>
            </AgentConfig>
          </data>
        </ServiceRequest>
        '''

        # Make the POST request for updating agent config
        response_update = requests.post(url_update, headers=headers_act_key, data=xml_data_update)

        # Check if the update was successful
        if '<responseCode>SUCCESS</responseCode>' in response_update.text:
            print("\nConfiguration profile updated successfully")
            print("\n\n**Important** - Agent scan merge and PM module must be enabled manually by editing the configuration profile")
        else:
            print("Failed to update configuration profile")
else:
    print("Error: Failed to create new configuration profile")
    print("\n########################## Start of Output ##########################\n")
    print(f"{response_create.text}")
    print("\n########################## End of Output ##########################\n\n")

# Define the data for creating inventory search list
data_command_for_inventory_search_list = {
    'action': 'create',
    'title': 'Inventory QIDs',
    'qids': '105237,105327,70030,70004,70022,45357,45208,90235,105311,45304,45017,82063,82040,6,70028,82044,82062,43007,45039,82023,82004,45038,45426,70053,70035,45179,90065,90195,45234,45456,105025,45303,12230,34011,78032,105194,38307,105053,105297,115263,70038,90035,90194,90331,90399,105015,45340-45351,45419,45006,48143'
}

# Define the data for creating discovery option profile
data_command_for_discovery_option_profile = {
    'action': 'create',
    'title': 'Discovery Profile',
    'global': '1',
    'scan_tcp_ports': 'standard',
    'scan_udp_ports': 'standard',
    'scan_parallel_scaling': '1',
    'vulnerability_detection': 'custom',
    'custom_search_list_title': 'Inventory QIDs',
    'basic_host_information_checks': '1',
    'basic_information_gathering': 'none',
    'enable_dissolvable_agent': '1',
    'ignore_firewall_generated_tcp_rst_packets': '1',
    'ignore_firewall_generated_tcp_syn_ack_packets': '1',
    'authentication': 'Windows,Unix'
}

# Define the URL for creating the inventory search list
url_to_create_search_list = f"{base_url}/api/2.0/fo/qid/search_list/static/"

# Define the URL for creating option profile
url_to_create_option_profile = f"{base_url}/api/2.0/fo/subscription/option_profile/vm/"

# Make requests for each command and print the response
response1 = requests.post(url_to_create_search_list,
                          auth=(username, password),
                          headers={'X-Requested-With': 'curl'},
                          data=data_command_for_inventory_search_list)

if response1.status_code == 200 and "New search list created successfully" in response1.text:
    print("\nSearch list created successfully")
else:
    print("Error: Failed to create new search list")
    print("\n########################## Start of Output ##########################\n")
    print(response1.text)
    print("\n########################## End of Output ##########################\n\n")

response2 = requests.post(url_to_create_option_profile,
                          auth=(username, password),
                          headers={'X-Requested-With': 'curl'},
                          data=data_command_for_discovery_option_profile)

if response2.status_code == 200 and "Option profile successfully added" in response2.text:
    print("\nOption profile created successfully")
else:
    print("Error: Failed to create new option profile")
    print("\n########################## Start of Output ##########################\n")
    print(response2.text)
    print("\n########################## End of Output ##########################\n\n")
