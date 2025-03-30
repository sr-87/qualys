# Qualys AutoTagger: Balance New Cloud Agent Hosts for Patching

The script automates the process of distributing tags for Qualys Cloud Agent hosts to facilitate balanced patch management. 

If you have regular patch jobs, like ones that run every day, the script spreads new Cloud Agent hosts across them. 

## Description
The script does the following:

### 1. Check the specified tags:

Checks that the specified tags exist in the Qualys account and they're static.

### 2. Identify new Cloud Agent hosts

Checks for new Cloud Agent deployments within the specified time frame.

### 3. Identifies Cloud Agent hosts that do not have the required tags

Checks for new Cloud Agent hosts that do not already have the specified tags.

### 4. Assigns tags 

Assigns the specified tags evenly across the new Cloud Agent hosts

## Features
- **Platform Selection**: Choose from multiple Qualys platforms (e.g., US1, US2, EU1, UK, etc.) to match your account’s region.

- **Secure Authentication**: Authenticates securely using username and password with Base64-encoded credentials.

- **Tag Validation**: Confirms that required UAT tags exist and are static.

- **New Host Retrieval**: Finds hosts created in the last 7 days with the "Cloud Agent" tag.

- **Balanced Distribution**: Counts hosts per tag and evenly assigns new hosts to balance the load.

- **Detailed Output**: Shows step-by-step results, including host details, tag counts, and assignment outcomes.

## Example Output
```
Options: US1, US2, US3, US4, UK, EU1, EU2, EU3, IN, CA, AE, AU, KSA
What platform is your account on? UK
Enter your username: myuser
Enter your password: 

Step 1: Checking for UAT tags and their type...

Existing UAT tags:
- UATMonday
- UATTuesday
- UATWednesday
- UATThursday

All required UAT tags are present and static

Step 2: Checking for recently created agent hosts...
Found 10 hosts:
ID: 54575363
Name: My Windows Asset 7
Created: 2025-03-29T12:22:41Z
Tags: OS: Windows Client, Testing, Type: Clients/Workstations



ID: 54575364
Name: My Windows Asset 8
Created: 2025-03-29T12:22:43Z
Tags: Type: Clients/Workstations, OS: Windows Client, Testing



ID: 54575553
Name: My Windows Asset 1
Created: 2025-03-29T12:22:31Z
Tags: OS: Windows Client, Testing, Type: Clients/Workstations



ID: 54575554
Name: My Windows Asset 4
Created: 2025-03-29T12:22:36Z
Tags: Testing, Type: Clients/Workstations, OS: Windows Client



ID: 54575555
Name: My Windows Asset 6
Created: 2025-03-29T12:22:40Z
Tags: OS: Windows Client, Testing, Type: Clients/Workstations



ID: 54575556
Name: My Windows Asset 9
Created: 2025-03-29T12:22:46Z
Tags: Type: Clients/Workstations, Testing, OS: Windows Client



ID: 54750564
Name: My Windows Asset 2
Created: 2025-03-29T12:22:32Z
Tags: OS: Windows Client, Testing, Type: Clients/Workstations



ID: 54750565
Name: My Windows Asset 3
Created: 2025-03-29T12:22:33Z
Tags: Type: Clients/Workstations, Testing, OS: Windows Client



ID: 54750566
Name: My Windows Asset 5
Created: 2025-03-29T12:22:39Z
Tags: Type: Clients/Workstations, OS: Windows Client, Testing



ID: 54750567
Name: My Windows Asset 10
Created: 2025-03-29T12:22:47Z
Tags: Testing, OS: Windows Client, Type: Clients/Workstations

Step 3: Checking hosts for UAT tags...
Found hosts without any UAT tags (proceeding to next step): 10 hosts:
ID: 54575363
Name: My Windows Asset 7
Created: 2025-03-29T12:22:41Z
Tags: OS: Windows Client, Testing, Type: Clients/Workstations



ID: 54575364
Name: My Windows Asset 8
Created: 2025-03-29T12:22:43Z
Tags: Type: Clients/Workstations, OS: Windows Client, Testing



ID: 54575553
Name: My Windows Asset 1
Created: 2025-03-29T12:22:31Z
Tags: OS: Windows Client, Testing, Type: Clients/Workstations



ID: 54575554
Name: My Windows Asset 4
Created: 2025-03-29T12:22:36Z
Tags: Testing, Type: Clients/Workstations, OS: Windows Client



ID: 54575555
Name: My Windows Asset 6
Created: 2025-03-29T12:22:40Z
Tags: OS: Windows Client, Testing, Type: Clients/Workstations



ID: 54575556
Name: My Windows Asset 9
Created: 2025-03-29T12:22:46Z
Tags: Type: Clients/Workstations, Testing, OS: Windows Client



ID: 54750564
Name: My Windows Asset 2
Created: 2025-03-29T12:22:32Z
Tags: OS: Windows Client, Testing, Type: Clients/Workstations



ID: 54750565
Name: My Windows Asset 3
Created: 2025-03-29T12:22:33Z
Tags: Type: Clients/Workstations, Testing, OS: Windows Client



ID: 54750566
Name: My Windows Asset 5
Created: 2025-03-29T12:22:39Z
Tags: Type: Clients/Workstations, OS: Windows Client, Testing



ID: 54750567
Name: My Windows Asset 10
Created: 2025-03-29T12:22:47Z
Tags: Testing, OS: Windows Client, Type: Clients/Workstations

Step 4: Counting assets and assigning tags...
Count for UATMonday: 0
Count for UATTuesday: 0
Count for UATWednesday: 0
Count for UATThursday: 0

Assigning 10 new assets to balance across all tags (target: 2 or 3)
Successfully assigned UATMonday (ID: 14556344) to host 54575363 (My Windows Asset 7)
Successfully assigned UATTuesday (ID: 14560699) to host 54575364 (My Windows Asset 8)
Successfully assigned UATMonday (ID: 14556344) to host 54575553 (My Windows Asset 1)
Successfully assigned UATTuesday (ID: 14560699) to host 54575554 (My Windows Asset 4)
Successfully assigned UATWednesday (ID: 14560700) to host 54575555 (My Windows Asset 6)
Successfully assigned UATThursday (ID: 14560702) to host 54575556 (My Windows Asset 9)
Successfully assigned UATMonday (ID: 14556344) to host 54750564 (My Windows Asset 2)
Successfully assigned UATTuesday (ID: 14560699) to host 54750565 (My Windows Asset 3)
Successfully assigned UATWednesday (ID: 14560700) to host 54750566 (My Windows Asset 5)
Successfully assigned UATThursday (ID: 14560702) to host 54750567 (My Windows Asset 10)

Updated counts after assignment:
Count for UATMonday: 3
Count for UATTuesday: 3
Count for UATWednesday: 2
Count for UATThursday: 2
```

## Usage

### Setup

Ensure you have Python 3.x installed along with the required libraries:
- `requests` for API calls
- `xml.etree.ElementTree` for XML parsing (included in Python’s standard library)
- `getpass` for secure password input (included in Python’s standard library)
- `datetime` for date handling (included in Python’s standard library)

### Run the Script
- Navigate to the directory with the script and run:
  ```sh
  python3 autoTagger.py
- Run the script, select your platform, and enter your Qualys credentials.
- The script will attempt to authenticate and then execute the above tasks.

## Error Handling

- **Invalid Platform**: Exits if an unrecognized platform is entered.

- **Authentication Failure**: Exits if login credentials are incorrect.

- **Missing/Dynamic Tags**: Exits if required tags are missing or are dynamic in nature.

- **API Errors**: Logs errors for failed requests or XML parsing issues and continues where possible.

- **No Recent Hosts**: Exits gracefully if no qualifying hosts are found.

## Notes

- **Permissions**: This script assumes you have API access and sufficient permissions in your Qualys account to manage tags and assets.

- **Credential Security**: Be cautious with your credentials; the script prompts for them at runtime and does not store them locally for security.

- **XML Payloads**: The script uses hardcoded XML payloads for API requests, designed for simplicity, but these can be modified to support additional filters or operations.

- **Tag Flexibility**: The script uses ***UATMonday***, ***UATTuesday***, ***UATWednesday***, and ***UATThursday*** as example tags for daily patch jobs. These must pre-existing in your Qualys environment and must be static. You can change them to any tags you prefer by updating the script’s tag list.

- **Time Window**: The 7-day window for new hosts is fixed but can be adjusted by modifying the days_back parameter in the `get_recent_agents()` function.

## Disclaimer

- Use at your own risk. This script interacts with the Qualys API which may have usage limits or require specific permissions. Always test in a non-production environment first.

## Feedback

Suggestions to update the script with additional features or commonly used tags are welcome. 

## Documentation

Qualys API documentation - https://www.qualys.com/documentation/
