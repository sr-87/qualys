# Qualys Asset Duplicate Detection

This Python script analyzes all assets in your Qualys subscription and identifies **potential duplicate assets** based on several common fields such as asset name, DNS name, MAC address, NetBIOS name, and IPv4 address.

It connects to the Qualys Gateway API using JWT authentication, retrieves all assets using paginated API calls, and performs multi-field duplicate analysis.  
A local JSON file containing all returned assets is also generated for review.

---

## Description

The script performs the following major steps:

### **1. Platform Selection**
Prompts the user to choose from all public Qualys platforms (US, EU, IN, AU, KSA, etc.).  
The script automatically maps the selected platform to the correct API gateway URL.

### **2. User Authentication**
Prompts for username and password using `getpass` to avoid exposing credentials.  
Authenticates using the `/auth` endpoint and retrieves a JWT token.

### **3. Asset Retrieval**
Fetches **all** assets from the Asset Management API (`/rest/2.0/search/am/asset`).  
Uses pagination (`pageSize` + `lastSeenAssetId`) to support large datasets.

### **4. Duplicate Detection**
Analyzes several fields for potential duplicates:

- Asset Name  
- DNS Name  
- NetBIOS Name  
- MAC Address  
- IPv4 Address  

Assets sharing the same normalized value in any category are grouped together and reported once.

### **5. Asset Export**
All retrieved assets are saved to: `all_assets.json`

This file can be used for offline review or reporting.

### **6. Logout / Session Invalidation**
The script calls the logout operation at the end to explicitly invalidate the active session token.

---

## Features

- **Supports all public Qualys platforms**
- **Secure credential input** (using `getpass`)
- **JWT authentication**
- **Full asset enumeration with pagination**
- **Cross-field duplicate detection**
- **Automatic JSON export**

---

## Requirements

Install the required Python libraries:

```
pip install requests
```

Modules used from the standard Python library:

- `json`
- `getpass`
- `itertools`
- `collections`

## Usage
**1. Run the script**
```
python3 duplicate_finder.py
```
**2. Select your Qualys platform**
Example: `US1`, `EU2`, `UK`, etc.

**3. Enter your Qualys username**

**4. Enter your Qualys password (hidden input)**

**5. The script will then:**

- Authenticate
- Retrieve all assets
- Detect potential duplicates and print on screen
- Save all fetched assets to `all_assets.json`
- Log out when complete

## Duplicate Detection Logic

Asset names, DNS names, MAC addresses, NetBIOS names, and IPv4 addresses are normalized and grouped. 

If more than one asset record shares the same values, the script reports them as a duplicate.

Duplicate records already reported for another field will not be repeated.

For example, if an asset is reported as a duplicate for DNS name match it will not be reported again as a duplicate for IPv4 address match.

The script does not modify any assets — all operations are read-only.

## Expected Output

Example block:
```
3 Potential duplicates based on Asset name

- Asset name: 'server01'
  * Asset ID: 12345
  * Asset ID: 98765
  * Asset ID: 47814
```

## Troubleshooting
**Authentication failed**
- Verify your username and password
- Ensure the correct platform was selected
- Confirm API access is enabled for your account

**No assets retrieved**
- Confirm the account has permissions to read assets

## Notes
- This script interacts with the Qualys Asset Management API and may be subject to API rate limits.
- No asset data is modified — the script is read-only.

## Disclaimer
This script is provided as a utility for detecting potential duplicate assets within your Qualys environment.
Use at your own discretion.
