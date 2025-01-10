# Qualys API Script for Tag Creation
This script automates the creation of asset tags in Qualys using the API. It's designed to be flexible, allowing users to select their Qualys platform, and then uses that selection to dynamically adjust API endpoints for authentication and tag creation.

## Description:
This script creates the following tag structure:

**OS: Operating Systems**
  - OS: Windows Server
  - OS: Windows Client
  - OS: Linux Server
  - OS: Linux Client
  - OS: Network OS

**Type: Asset Types**
  - Type: Servers
  - Type: Database Servers
  - Type: Domain Controllers
  - Type: Clients/Workstations
  - Type: Network Devices
  - Type: Printers

## Features
- **Platform Selection:** Choose from all public Qualys platforms (US1, US2, US3, US4, UK, EU1, EU2, EU3, IN, CA, AE, AU, KSA) to set the correct base URL for API calls.
- **User Authentication:** Securely prompts for username and password using Python's ```getpass``` module to avoid echoing passwords in the console.
- **Tag Creation:** 
  - Creates parent tags for "OS: Operating Systems" and "Type: Asset Types".
  - Automatically generates child tags under these categories based on predefined rules and criticality scores.

## Usage
1. **Setup:** Ensure you have Python installed with required libraries (requests, xml.etree.ElementTree).
2. **Run the Script:**
  - Run the script, select your platform, and enter your Qualys credentials.
  - The script will attempt to authenticate and then create the specified tags.

## Requirements
- Python 3.x
- ```requests``` library
- ```xml.etree.ElementTree``` for XML parsing (included in Python's standard library)

## Notes
- This script assumes you have permission to create tags within your Qualys account. 
- Be cautious with your credentials; this script does not include any form of local credential storage for security reasons.
- The script uses XML payloads for tag creation which are hardcoded for simplicity but can be modified or expanded for different needs.

## Disclaimer
Use at your own risk. This script interacts with the Qualys API which may have usage limits or require specific permissions. Always test in a non-production environment first. 

## Feedback
Suggestions to update the script with other commonly used tags are welcome. If you have suggestions or improvements, please feel free to open an issue or submit a pull request on GitHub.
