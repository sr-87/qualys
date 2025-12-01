# Qualys Asset Duplicate Detection

This Python script analyzes all host assets in your Qualys subscription and identifies **potential duplicate assets** based on several common fields such as asset name, DNS name, MAC address, NetBIOS name, and IPv4 address.

It connects to the Qualys Gateway API using JWT authentication, retrieves all assets using paginated API calls, and performs multi-field duplicate analysis. The script generates both an **Excel spreadsheet** and an **interactive HTML report** for easy review and sharing.

---

## How It Works

1. **Platform Selection** - Choose from all public Qualys platforms (US1-4, UK, EU1-3, IN, CA, AE, AU, KSA)
2. **Authentication** - Secure login using JWT token
3. **Asset Retrieval** - Fetches all assets with pagination support
4. **Duplicate Detection** - Analyzes Asset Name, DNS Name, NetBIOS Name, MAC Address, and IPv4 Address
5. **Report Generation** - Creates Excel and HTML reports with timestamped filenames
6. **Session Cleanup** - Invalidates JWT token upon completion

**Important:** The account used must have:
- **API access enabled**
- **MFA (Multi-Factor Authentication) disabled** - MFA is not compatible with API authentication

---

## Requirements

- Python 3.6 or higher
- Dependencies: `requests`, `openpyxl`

**Installation:**
```bash
pip install requests openpyxl
```

Or if using `pip3`:
```bash
pip3 install requests openpyxl
```

**Account Requirements:**
- API access enabled
- MFA disabled
- Asset Management read permissions

---

## Usage

```bash
python3 duplicate_finder.py
```

Follow the prompts to:
1. Select your Qualys platform (US1, EU2, UK, IN, etc.)
2. Enter username and password

The script will authenticate, fetch assets, detect duplicates, and generate reports in the current directory.

---

## Output

### **Excel Report** (`duplicate_assets_YYYYMMDD_HHMMSS.xlsx`)
- Frozen headers
- Color-coded duplicate groups (alternating blue/peach)
- Columns: Asset ID, Address, DNS Name, Asset Name, Source

### **HTML Report** (`duplicate_assets_YYYYMMDD_HHMMSS.html`)
- Summary dashboard with metrics
- Real-time search across all columns
- Sortable and resizable columns
- Reset sort button
- Print-friendly layout

---

## Duplicate Detection Logic

Assets sharing the same normalized value in any field are grouped as duplicates:
- Asset Name, DNS Name, NetBIOS Name, MAC Address
- IPv4 Address (used as-is)

**Tracking:** Duplicate pairs are only reported once across all fields to prevent redundant alerts.

**Coloring:** Each duplicate group gets alternating colors (blue/peach) for easy visual identification.

**Read-Only:** The script does not modify any assets.

---


## Supported Qualys Platforms

| Platform Code | Region | Gateway URL |
|---------------|--------|-------------|
| US1 | United States | gateway.qg1.apps.qualys.com |
| US2 | United States | gateway.qg2.apps.qualys.com |
| US3 | United States | gateway.qg3.apps.qualys.com |
| US4 | United States | gateway.qg4.apps.qualys.com |
| UK | United Kingdom | gateway.qg1.apps.qualys.co.uk |
| EU1 | Europe | gateway.qg1.apps.qualys.eu |
| EU2 | Europe | gateway.qg2.apps.qualys.eu |
| EU3 | Europe (Italy) | gateway.qg3.apps.qualys.it |
| IN | India | gateway.qg1.apps.qualys.in |
| CA | Canada | gateway.qg1.apps.qualys.ca |
| AE | United Arab Emirates | gateway.qg1.apps.qualys.ae |
| AU | Australia | gateway.qg1.apps.qualys.com.au |
| KSA | Kingdom of Saudi Arabia | gateway.qg1.apps.qualysksa.com |

---

## Troubleshooting

**Authentication failed**
- Verify username/password and platform selection
- Confirm API access enabled and MFA disabled

**No assets retrieved**
- Check Asset Management read permissions
- Verify assets exist in subscription

**Module not found**
```bash
pip install requests openpyxl
```
Or:
```bash
pip3 install requests openpyxl
```

**Large datasets**
- Fetches 300 assets per call (maximum)
- Progress updates displayed during fetch

---

## Notes

- Credentials entered at runtime are not stored
- JWT tokens expire after 4 hours
- Report files may contain sensitive data - handle securely
- Script is read-only and does not modify assets
- Manual review of duplicates recommended before taking action

---

## Version History

### **v1.5**
- Added interactive HTML report generation
- Added Excel export with color-coded groups
- Added summary metrics (total assets, duplicates, percentage)
- Added source tracking for assets
- Enhanced terminal output formatting
- Improved duplicate pair tracking algorithm
- Added session logout functionality

### **v1.0**
- JSON export only
- Basic duplicate detection across 5 fields
- Terminal-only output

---

## Disclaimer

This script is provided as a utility for detecting potential duplicate assets within your Qualys environment.
Use at your own discretion. Always review identified duplicates manually before taking action in your Qualys subscription.

---

## Support

For issues, questions, or feature requests, please open an issue in the repository.
