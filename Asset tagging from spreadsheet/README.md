# Qualys Asset Tagging from Spreadsheet

This Python script, **"Asset tagging from spreadsheet,"** automates the bulk application of tags to assets. 

It reads asset names and a list of desired tags from an external Excel/CSV file, verifies their existence in Qualys, and updates the corresponding assets with any new tags.

---

## Description

The script performs the following core actions:

1.  **Read Input File:** Reads asset names and a comma-separated list of tags from the user-specified file name.
2.  **Asset Identification:** Searches the Qualys platform using the Asset Name to retrieve the unique Qualys Asset ID and list of existing tags.
3.  **Tag Lookup:** Searches Qualys for each desired tag to retrieve its unique Tag ID.
4.  **Tag Application:** Adds all newly identified tags to the asset.
5.  **Reporting:** Provides detailed output for each asset, confirming which tags were applied and which were skipped (e.g., already applied or tag not found).

---

## Features

* **Platform Selection:** Choose from all public Qualys platforms (US1, US2, EU1, etc.) to set the correct base URL for API calls.
* **User Authentication:** Securely prompts for username and password using Python's `getpass` module.
* **Duplicate Detection:** Automatically checks if a tag is already applied to an asset before attempting an update.
* **Error Handling:** Gracefully handles missing files, authentication failures, and API errors.

---

## Input File Requirements

The script is currently **hard-coded** to look for a specific file name (e.g., `Assets_needing_tags.xlsx`) and expects it to be placed in the same directory as the script. 

Please ensure the file name in the script's code matches the file you intend to use.

### File Format

| Column | Data Expected | Description |
|:---|:---|:---|
| **A (Index 0)** | Asset Name (String) | The exact name of the asset as it appears in Qualys. |
| **B (Index 1)** | Desired Tags (String) | A comma-separated list of tag names to be applied to the asset. |

### Important Notes

* **No Header Row:** The script reads data starting from the **first row** (row 1). Do not include column headers.
* **Tag Separator:** Tags in Column B **must be separated by commas** (e.g., `Linux, Server, Environment:Prod`).
* **Empty Rows:** Empty rows (where Column A is blank) are automatically skipped.

### Example File Content

Your Excel file should look like this:

| Column A | Column B |
|:---------|:---------|
| server01.example.com | Linux, Production, WebServer |
| server02.example.com | Windows, Development |
| server03.example.com | Database, Production, Critical |

**Visual representation of the Excel file:**
```
┌─────────────────────────┬──────────────────────────────────┐
│ server01.example.com    │ Linux, Production, WebServer     │
├─────────────────────────┼──────────────────────────────────┤
│ server02.example.com    │ Windows, Development             │
├─────────────────────────┼──────────────────────────────────┤
│ server03.example.com    │ Database, Production, Critical   │
└─────────────────────────┴──────────────────────────────────┘
```

---

## Usage

### 1. Setup

Ensure you have **Python 3.x** installed with the required libraries:
```bash
pip install requests pandas openpyxl
```

**Required Libraries:**
- `requests` - For HTTP API calls
- `pandas` - For reading Excel files
- `openpyxl` - Required by pandas to read `.xlsx` files
- `xml.etree.ElementTree` - For XML parsing (included in Python standard library)

### 2. Prepare Input File

1. Create or update the required input file (e.g., `Assets_needing_tags.xlsx`) following the column format described above.
2. Ensure Column A contains the correct Asset Name and Column B contains the comma-separated tags.

### 3. Run the Script

1. Navigate to the directory containing the script and the input file.
2. Run the script:
```bash
python3 "tag_from_spreadsheet.py"
```

3. Follow the prompts:
   - Select your Qualys platform (e.g., `US1`, `EU1`)
   - Enter your Qualys username
   - Enter your Qualys password (hidden input)
  
### 4. Review Output

The script provides detailed output for each asset:
```
Asset name: server01.example.com
New tags applied: Linux, WebServer
Tags not applied: None
```

---

## Output Examples

**Successful tagging:**
```
Asset name: server01.example.com
New tags applied: Linux, Production
Tags not applied: None
```

**Tag already exists:**
```
Asset name: server02.example.com
New tags applied: Development
Tags not applied: None
```
*(Production was already applied, so only Development was added)*

**Tag not found in Qualys:**
```
Amazon name: server03.example.com
New tags applied: Database
Tags not applied: NonExistentTag
```

---

## Requirements

* **Qualys Permissions:** The account used must have permissions to:
  - Search for assets in Asset Management
  - Search for tags in Asset Management
  - Update assets with new tags
 
---

## Troubleshooting

**"File not found" error:**
- Ensure `Assets_needing_tags.xlsx` is in the same directory as the script
- Check the file name matches exactly (case-sensitive on Linux/Mac)

**"Authentication failed" error:**
- Verify your username and password are correct
- Confirm you selected the correct platform
- Check that your account has API access enabled

**"No asset found" message:**
- Verify the asset name in Column A exactly matches the name in Qualys
- Asset names are case-sensitive

**"No tag found" message:**
- Verify the tag exists in your Qualys account
- Check for typos in tag names
- Tag names are case-sensitive

---

## Notes

* This script uses Basic Authentication, which requires permissions to search for assets/tags and update assets within your Qualys account.
* The script includes a logout operation at the end to close the authenticated session.

---

## Disclaimer

Use at your own risk. 

Always test this script in a non-production environment first and with limited assets.

The script interacts with the Qualys API and is subject to usage limits and required permissions.
