# Qualys API Script for new account configuration

This script automates several tasks within the Qualys platform such as the creation of tags, cloud agent activation key, cloud agent configuration profile, search list with inventory QIDs, and Option Profile for discovery.

It's designed to be flexible, allowing users to select their Qualys platform before executing API calls.

## Description

The script creates the following:

### 1. Tags:
#### OS: Operating Systems
- OS: Windows Server
- OS: Windows Client
- OS: Linux Server
- OS: Linux Client
- OS: Network OS

#### Type: Asset Types
- Type: Servers
- Type: Database Servers
- Type: Domain Controllers
- Type: Clients/Workstations
- Type: Network Devices
- Type: Printers

### 2. Cloud Agent Activation Key:
- **Title**: Default Key
- **Activated modules**: VM, PM, SCA, GAV/CSAM

### 3. Cloud Agent Configuration Profile:
- **Order**: 1
- **Title**: Default
- **Make this the default profile for the subscription**: yes
- **Performance customization**: On
- **Based On**: Low
- **Agent Status Interval**: 900 seconds
- **Delta Upload Interval**: 5 seconds
- **Chunk sizes for file fragment uploads**: 4096 KB
- **Upgrade Reattempt Interval**: 32400 seconds
- **Logging level for agent**: Verbose
- **Priority Status Upload Interval**: 300
- **CPU Limit**: 10%
- **Agent Scan Merge**: Off
- **PM  Module**: Off

Other settings remain at the default

### 4. Inventory Search List:
- **Title**:Inventory QIDs
- **QIDs**:
  - 6 - DNS Host Name
  - 12230 - Default Web Page
  - 34011 - Firewall Detected
  - 38307 - Unix Authentication Method
  - 43007 - Network Adapter MAC Address
  - 45006 - Traceroute
  - 45017 - Operating System Detected
  - 45038 - Host Scan Time - Scanner
  - 45039 - Host Names Found
  - 45179 - Report Qualys Host ID Value
  - 45208 - System and BaseBoard Serial Numbers
  - 45234 - Hyper-V Host Information Gathered From A Windows Virtual Machine
  - 45303 - System Management BIOS UUID Detected
  - 45304 - Model Information from Devices
  - 45340 - Microsoft Windows 7 Operating System Detected
  - 45341 - Microsoft Windows Server 2008 Operating System Detected
  - 45342 - Microsoft Windows 10 Operating System Detected
  - 45343 - Microsoft Windows Server 2008 Core Operating System Detected
  - 45344 - Microsoft Windows 8 Operating System Detected
  - 45345 - Microsoft Windows Server 2008 R2 Operating System Detected
  - 45346 - Microsoft Windows 8.1 Operating System Detected
  - 45347 - Microsoft Windows Server 2016 Operating System Detected
  - 45348 - Microsoft Windows Server 2012 R2 Operating System Detected
  - 45349 - Microsoft Windows Server 2016 Core Operating System Detected
  - 45350 - Microsoft Windows Server 2012 Core Operating System Detected
  - 45351 - Microsoft Windows Server 2012 Operating System Detected
  - 45357 - Display BIOS Asset Tag - Chassis
  - 45419 - Microsoft Windows Server 2019 Operating System Detected
  - 45426 - Scan Activity per Port
  - 45456 - Windows WMI AuthenticationLevel Status
  - 48143 - Qualys Correlation ID Detected
  - 70004 - NetBIOS Bindings Information
  - 70022 - Open DCE-RPC / MS-RPC Services List
  - 70028 - Windows Authentication Method
  - 70030 - NetBIOS Shared Folders
  - 70035 - Windows Login User Information
  - 70038 - File and Print Services Access Denied
  - 70053 - Windows Authentication Method for User-Provided Credentials
  - 78032 - Wireless Access Point Information
  - 82004 - Open UDP Services List
  - 82023 - Open TCP Services List
  - 82040 - ICMP Replies Received
  - 82044 - NetBIOS Host Name
  - 82062 - NetBIOS Workgroup Name Detected
  - 82063 - Host Uptime Based on TCP TimeStamp Option
  - 90035 - Missing AllowedPaths Registry Key
  - 90065 - Windows Services List
  - 90194 - Windows Registry Pipe Access Level
  - 90195 - Windows Registry Key Access Denied
  - 90235 - Installed Applications Enumerated From Windows Installer
  - 90331 - Access to File Share is Enabled
  - 90399 - Windows File Access Denied
  - 105015 - Windows Authentication Failed
  - 105025 - Windows Registry Access Level
  - 105053 - Unix Authentication Failed
  - 105237 - SAMR Pipe Permissions Enumerated
  - 105297 - Unix Authentication Not Attempted
  - 105311 - Last Successful User Login
  - 105327 - Antivirus Product Detected on Windows Host
  - 115263 - Unix Authentication Timeout Occurred

### 5. Option Profile for Discovery scans:
- **Title**:Discovery Profile
- **Vulnerability Detection**: Custom
- **Include the QIDs from the selected lists** Inventory QIDs

Other settings remain at the default

## Features

- **Platform Selection**: Choose from all public Qualys platforms (US1, US2, US3, US4, UK, EU1, EU2, EU3, IN, CA, AE, AU, KSA) to set the correct base URL for API calls.
- **User Authentication**: Securely prompts for username and password using Python's `getpass` module to avoid echoing passwords in the console.
- **Tag Creation**: 
  - Creates parent tags for "OS: Operating Systems" and "Type: Asset Types".
  - Automatically generates child tags under these categories based on predefined rules and criticality scores.
- **Activation Key & Configuration**: 
  - Generates a new Cloud Agent Activation Key with specific modules enabled.
  - Creates a new Cloud Agent Configuration Profile with recommended settings.
- **Inventory and Discovery Management**: 
  - Constructs a Search List with inventory QIDs.
  - Sets up an Option Profile for asset discovery.

## Important Note on Configuration Settings

**Agent Scan Merge** and **PM Module** cannot be enabled through the API with this script. After running the script, you must manually edit your configuration profile in the Qualys interface to:

- **Enable Agent Scan Merge**: This feature helps in merging scan results from the agent and the scanner appliance.
- **Enable PM Module**: This ensures that Patch Management capabilities are enabled on the asset.

Please navigate to the Qualys portal, find your configuration profile, and toggle these settings on.

## Usage

### Setup
- Ensure you have **Python 3.x** installed with required libraries:
  - `requests`
  - `xml.etree.ElementTree` (included in Python's standard library)

### Run the Script
- Navigate to the directory with the script and run:
  ```sh
  python3 script_name.py
- Run the script, select your platform, and enter your Qualys credentials.
- The script will attempt to authenticate and then execute the above tasks.

## Requirements

- Python 3.x
- `requests` library
- `xml.etree.ElementTree` for XML parsing (included in Python's standard library)

## Notes

- This script assumes you have permission to perform these operations within your Qualys account.
- Be cautious with your credentials; this script does not include any form of local credential storage for security reasons.
- The script uses XML payloads for various operations which are hardcoded for simplicity but can be modified or expanded.

## Disclaimer

- Use at your own risk. This script interacts with the Qualys API which may have usage limits or require specific permissions. Always test in a non-production environment first.

## Feedback

Suggestions to update the script with additional features or commonly used tags are welcome. If you have suggestions or improvements, please feel free to open an issue or submit a pull request on GitHub.

## Documentation

Qualys API documentation - https://www.qualys.com/documentation/
