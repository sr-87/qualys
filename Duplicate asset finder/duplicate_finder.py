import requests
import json
import getpass
from collections import defaultdict
from itertools import combinations
from openpyxl import Workbook
from openpyxl.styles import PatternFill, Font, Alignment

# Ask for the platform selection
print("\nOptions: US1, US2, US3, US4, UK, EU1, EU2, EU3, IN, CA, AE, AU, KSA\n")
platform = input("What platform is your account on? ").upper()

# Define gateway URLs for each platform
gateway_urls = {
    "US1": "https://gateway.qg1.apps.qualys.com",
    "US2": "https://gateway.qg2.apps.qualys.com",
    "US3": "https://gateway.qg3.apps.qualys.com",
    "US4": "https://gateway.qg4.apps.qualys.com",
    "UK": "https://gateway.qg1.apps.qualys.co.uk",
    "EU1": "https://gateway.qg1.apps.qualys.eu",
    "EU2": "https://gateway.qg2.apps.qualys.eu",
    "EU3": "https://gateway.qg3.apps.qualys.it",
    "IN": "https://gateway.qg1.apps.qualys.in",
    "CA": "https://gateway.qg1.apps.qualys.ca",
    "AE": "https://gateway.qg1.apps.qualys.ae",
    "AU": "https://gateway.qg1.apps.qualys.com.au",
    "KSA": "https://gateway.qg1.apps.qualysksa.com"
}

# Select the correct gateway URL
if platform in gateway_urls:
    gateway_url = gateway_urls[platform]
else:
    print("Invalid platform selection. Exiting")
    exit(1)  # Exit if platform detail is incorrect

# Input for username and password at runtime
username = input("Enter your username: ")
password = getpass.getpass("Enter your password: ")

# Define the authentication URL using the gateway URL
auth_url = f"{gateway_url}/auth"

# Authentication headers and data for JWT
auth_headers = {
    "Content-Type": "application/x-www-form-urlencoded"
}
auth_data = {
    "username": username,
    "password": password,
    "token": "true"
}

# Perform authentication to get JWT
auth_response = requests.post(auth_url, headers=auth_headers, data=auth_data)
if auth_response.status_code != 201:
    print(f"Authentication failed. (HTTP {auth_response.status_code}).")
    print("Response from server:")
    print(auth_response.text or "No additional error details provided.")
    exit(1)

# Extract JWT token from response body (plain string)
jwt_token = auth_response.text.strip()
print("\nAuthentication successful.")

# Now fetch all assets using the asset endpoint
asset_url = f"{gateway_url}/rest/2.0/search/am/asset"
asset_headers = {
    "Accept": "application/json",
    "Authorization": f"Bearer {jwt_token}",
    "Content-Type": "application/json"
}

print("\nFetching assets...")

all_assets = []
last_seen_asset_id = None
has_more = True
page_size = 300  # Max allowed for fewer calls

while has_more:
    params = {"pageSize": page_size}
    if last_seen_asset_id:
        params["lastSeenAssetId"] = last_seen_asset_id

    asset_response = requests.post(asset_url, headers=asset_headers, params=params, json={})

    if asset_response.status_code != 200:
        print(f"Failed to fetch assets (HTTP {asset_response.status_code}).")
        print("Response from server:")
        print(asset_response.text or "No additional error details provided.")
        exit(1)

    data = asset_response.json()
    assets = data.get("assetListData", {}).get("asset", [])
    all_assets.extend(assets)

    current_has_more = data.get("hasMore", 0) == 1
    current_last_seen = data.get("lastSeenAssetId")

    print(f"\nFetched {len(all_assets)} assets so far...")

    has_more = current_has_more
    last_seen_asset_id = current_last_seen

# Check for potential duplicates across multiple fields
print("\nChecking for potential duplicates...\n")

# Track flagged duplicate pairs (as frozensets of asset IDs) to avoid repeats
flagged_pairs = set()

# List to collect all duplicate assets for CSV export
csv_data = []
# Track which duplicate group each CSV row belongs to (for coloring)
csv_row_to_group = []
# Track which assets have already been added to avoid duplicates in the file
added_assets = set()

# Field display names and getters
fields = [
    ("assetName", "Asset name", lambda x: str(x.get("assetName") or "").strip().lower()),
    ("dnsName", "DNS name", lambda x: str(x.get("dnsName") or "").strip().lower()),
    ("netBIOSName", "NetBIOS name", lambda x: str(x.get("netBIOSName") or "").strip().lower()),
    ("macAddress", "MAC address", lambda x: str(x.get("macAddress") or "").strip().lower()),
    ("ipv4Address", "IPv4 address", lambda x: str(x.get("address") or "").strip())
]

for field_name, display_name, normalize_func in fields:
    groups = defaultdict(list)
    for asset in all_assets:
        value = normalize_func(asset)
        if value:  # Only consider non-empty values
            asset_id = asset.get("assetId")
            if asset_id is not None:  # Ensure assetId exists
                groups[value].append({
                    "asset_id": asset_id,
                    "asset": asset
                })
    
    new_duplicates = []
    for value, group in groups.items():
        if len(group) > 1:
            # Check if this group has any new pairs not flagged
            group_ids = [item["asset_id"] for item in group]
            group_pairs = [frozenset([id1, id2]) for id1, id2 in combinations(group_ids, 2)]
            if all(pair not in flagged_pairs for pair in group_pairs):
                new_duplicates.append((value, group))
                # Flag all pairs in this group
                for pair in group_pairs:
                    flagged_pairs.add(pair)
    
    num_duplicates = len(new_duplicates)
    if field_name == "assetName":
        print(f"--------------------------------------------------------------------")
        print(f"\n{num_duplicates} Potential duplicates based on {display_name}")
    else:
        print(f"--------------------------------------------------------------------")
        print(f"\n{num_duplicates} Potential duplicates based on {display_name}, not reported previously\n")
    
    if num_duplicates > 0:
        for value, group in new_duplicates:
            print(f"\n- {display_name}: '{value}'")
            # Get current group number for coloring
            if len(csv_row_to_group) == 0:
                current_group_num = 0
            else:
                # Get the last group number and increment it
                current_group_num = csv_row_to_group[-1] + 1

            for item in group:
                asset = item['asset']
                asset_id = item['asset_id']

                # Extract all sources from inventoryListData
                inventory_list = asset.get('inventoryListData', {})
                inventory_items = inventory_list.get('inventory', [])
                if inventory_items and len(inventory_items) > 0:
                    sources = [item.get('source', 'Unknown') for item in inventory_items]
                    source = ', '.join(sources)
                else:
                    source = 'Unknown'

                # Extract fields for CSV
                address = asset.get('address', '')
                dns_name = asset.get('dnsName', '')
                asset_name = asset.get('assetName', '')

                # Only add to CSV if this asset hasn't been added before
                if asset_id not in added_assets:
                    csv_data.append({
                        'Asset ID': asset_id,
                        'Address': address,
                        'DNS Name': dns_name,
                        'Asset Name': asset_name,
                        'Source': source
                    })
                    # Track group number for this row (for coloring in Excel)
                    csv_row_to_group.append(current_group_num)
                    # Mark this asset as added
                    added_assets.add(asset_id)

                # Format output with asset name for non-assetName duplicates
                if field_name == "assetName":
                    # Don't include asset name in output as it would be redundant
                    print(f"  * Asset ID: {asset_id} (Source: {source})")
                else:
                    # Include asset name in output
                    asset_name_display = asset_name if asset_name else "(unavailable)"
                    print(f"  * Asset ID: {asset_id} | Asset name: {asset_name_display} | (Source: {source})")

# Calculate total number of unique duplicate assets
unique_duplicate_assets = set()
for pair in flagged_pairs:
    unique_duplicate_assets.update(pair)
total_duplicates = len(unique_duplicate_assets)

print(f"\n--------------------------------------------------------------------")
print(f"\nTotal potential duplicate assets found: {total_duplicates}\n")

# Write duplicate assets to Excel file with alternating colors
if csv_data:
    import os
    from datetime import datetime

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    excel_filename = f"duplicate_assets_{timestamp}.xlsx"
    excel_filepath = os.path.abspath(excel_filename)

    # Create workbook and worksheet
    wb = Workbook()
    ws = wb.active
    ws.title = "Duplicate Assets"

    # Define colors for alternating groups
    color1 = PatternFill(start_color="AED6F1", end_color="AED6F1", fill_type="solid")  # Medium light blue
    color2 = PatternFill(start_color="FAD7A0", end_color="FAD7A0", fill_type="solid")  # Light peach/orange

    # Header styling
    header_fill = PatternFill(start_color="34495E", end_color="34495E", fill_type="solid")  # Dark blue-gray
    header_font = Font(bold=True, color="FFFFFF", size=11)
    header_alignment = Alignment(horizontal="center", vertical="center")

    # Write headers
    headers = ['Asset ID', 'Address', 'DNS Name', 'Asset Name', 'Source']
    for col_num, header in enumerate(headers, 1):
        cell = ws.cell(row=1, column=col_num, value=header)
        cell.fill = header_fill
        cell.font = header_font
        cell.alignment = header_alignment

    # Write data rows with alternating colors per group
    row_num = 2
    for idx, row_data in enumerate(csv_data):
        # Get the group number for this row
        group_num = csv_row_to_group[idx]

        # Alternate color based on group number
        row_fill = color1 if group_num % 2 == 0 else color2

        # Write row data
        ws.cell(row=row_num, column=1, value=row_data['Asset ID']).fill = row_fill
        ws.cell(row=row_num, column=2, value=row_data['Address']).fill = row_fill
        ws.cell(row=row_num, column=3, value=row_data['DNS Name']).fill = row_fill
        ws.cell(row=row_num, column=4, value=row_data['Asset Name']).fill = row_fill
        ws.cell(row=row_num, column=5, value=row_data['Source']).fill = row_fill

        row_num += 1

    # Auto-size columns
    for column in ws.columns:
        max_length = 0
        column_letter = column[0].column_letter
        for cell in column:
            try:
                if cell.value:
                    max_length = max(max_length, len(str(cell.value)))
            except:
                pass
        adjusted_width = min(max_length + 2, 50)  # Cap at 50 characters
        ws.column_dimensions[column_letter].width = adjusted_width

    # Freeze the header row
    ws.freeze_panes = "A2"

    # Save the workbook
    wb.save(excel_filename)

    excel_directory = os.path.dirname(excel_filepath)
    print(f"Duplicate assets exported to {excel_filename}\n")
    print(f"File located at {excel_directory}\n")

    # Generate HTML report
    html_filename = f"duplicate_assets_{timestamp}.html"
    html_filepath = os.path.abspath(html_filename)

    html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Duplicate Assets Report - {timestamp}</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}

        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
            background: linear-gradient(135deg, #224F91 0%, #1a3d73 100%);
            padding: 20px;
            min-height: 100vh;
        }}

        .container {{
            max-width: 1400px;
            margin: 0 auto;
            background: white;
            border-radius: 12px;
            box-shadow: 0 20px 60px rgba(0,0,0,0.3);
            overflow: hidden;
        }}

        .header {{
            background: linear-gradient(135deg, #34495E 0%, #2C3E50 100%);
            color: white;
            padding: 30px;
            text-align: center;
        }}

        .header h1 {{
            font-size: 28px;
            margin-bottom: 10px;
        }}

        .header .metadata {{
            font-size: 14px;
            opacity: 0.9;
            margin-top: 10px;
        }}

        .summary {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            padding: 30px;
            background: #f8f9fa;
            border-bottom: 2px solid #e9ecef;
        }}

        .summary-card {{
            background: white;
            padding: 20px;
            border-radius: 8px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
            text-align: center;
        }}

        .summary-card .number {{
            font-size: 36px;
            font-weight: bold;
            color: #224F91;
            margin-bottom: 5px;
        }}

        .summary-card .label {{
            font-size: 14px;
            color: #6c757d;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }}

        .controls {{
            padding: 20px 30px;
            background: white;
            border-bottom: 1px solid #e9ecef;
            display: flex;
            gap: 15px;
            align-items: center;
            flex-wrap: wrap;
        }}

        .search-box {{
            flex: 1;
            min-width: 250px;
            position: relative;
        }}

        .search-box input {{
            width: 100%;
            padding: 10px 15px 10px 40px;
            border: 2px solid #e9ecef;
            border-radius: 6px;
            font-size: 14px;
            transition: border-color 0.3s;
        }}

        .search-box input:focus {{
            outline: none;
            border-color: #224F91;
        }}

        .search-box::before {{
            content: "🔍";
            position: absolute;
            left: 12px;
            top: 50%;
            transform: translateY(-50%);
        }}

        .table-container {{
            padding: 30px;
            overflow-x: auto;
        }}

        table {{
            width: 100%;
            border-collapse: collapse;
            background: white;
        }}

        thead {{
            background: #34495E;
            color: white;
            position: sticky;
            top: 0;
            z-index: 10;
        }}

        th {{
            padding: 15px;
            text-align: left;
            font-weight: 600;
            font-size: 13px;
            text-transform: uppercase;
            letter-spacing: 0.5px;
            cursor: pointer;
            user-select: none;
            white-space: nowrap;
            position: relative;
        }}

        th .resizer {{
            position: absolute;
            top: 0;
            right: 0;
            width: 5px;
            cursor: col-resize;
            user-select: none;
            height: 100%;
        }}

        th .resizer:hover {{
            background-color: #224F91;
        }}

        th:hover {{
            background: #2C3E50;
        }}

        th::after {{
            content: " ⇅";
            opacity: 0.5;
            font-size: 10px;
        }}

        td {{
            padding: 12px 15px;
            border-bottom: 1px solid #f0f0f0;
            font-size: 14px;
        }}

        tr.group-0 {{
            background-color: #AED6F1;
        }}

        tr.group-1 {{
            background-color: #FAD7A0;
        }}

        tr:hover {{
            opacity: 0.8;
            transition: opacity 0.2s;
        }}

        .no-results {{
            text-align: center;
            padding: 40px;
            color: #6c757d;
            font-size: 16px;
        }}

        .footer {{
            text-align: center;
            padding: 20px;
            background: #f8f9fa;
            color: #6c757d;
            font-size: 13px;
            border-top: 1px solid #e9ecef;
        }}

        .legend {{
            display: flex;
            gap: 20px;
            align-items: center;
            font-size: 13px;
        }}

        .legend-item {{
            display: flex;
            align-items: center;
            gap: 8px;
        }}

        .legend-color {{
            width: 24px;
            height: 24px;
            border-radius: 4px;
            border: 1px solid #ddd;
        }}

        .btn {{
            padding: 10px 20px;
            background: #224F91;
            color: white;
            border: none;
            border-radius: 6px;
            cursor: pointer;
            font-size: 14px;
            transition: background 0.3s;
        }}

        .btn:hover {{
            background: #1a3d73;
        }}

        @media print {{
            body {{
                background: white;
                padding: 0;
            }}

            .controls, .btn {{
                display: none;
            }}

            .container {{
                box-shadow: none;
            }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>Duplicate Assets Report</h1>
            <div class="metadata">
                User: {username} | Generated: {datetime.now().strftime("%d-%m-%Y %H:%M:%S")}
            </div>
        </div>

        <div class="summary">
            <div class="summary-card">
                <div class="number">{len(all_assets)}</div>
                <div class="label">Host Assets</div>
            </div>
            <div class="summary-card">
                <div class="number">{total_duplicates}</div>
                <div class="label">Potential Duplicates</div>
            </div>
            <div class="summary-card">
                <div class="number">{round((total_duplicates / len(all_assets) * 100), 1) if len(all_assets) > 0 else 0}%</div>
                <div class="label">Duplicate Ratio</div>
            </div>
        </div>

        <div class="controls">
            <div class="search-box">
                <input type="text" id="searchInput" placeholder="Search by Asset ID, Address, DNS Name, Asset Name, or Source...">
            </div>
            <button class="btn" id="resetSortBtn">Reset Sort</button>
            <button class="btn" onclick="window.print()">Print Report</button>
        </div>

        <div class="table-container">
            <table id="dataTable">
                <thead>
                    <tr>
                        <th data-column="0">Asset ID<div class="resizer"></div></th>
                        <th data-column="1">Address<div class="resizer"></div></th>
                        <th data-column="2">DNS Name<div class="resizer"></div></th>
                        <th data-column="3">Asset Name<div class="resizer"></div></th>
                        <th data-column="4">Source<div class="resizer"></div></th>
                    </tr>
                </thead>
                <tbody>
"""

    # Add table rows
    for idx, row_data in enumerate(csv_data):
        group_num = csv_row_to_group[idx]
        group_class = f"group-{group_num % 2}"

        html_content += f"""                    <tr class="{group_class}" data-original-index="{idx}">
                        <td>{row_data['Asset ID']}</td>
                        <td>{row_data['Address']}</td>
                        <td>{row_data['DNS Name']}</td>
                        <td>{row_data['Asset Name']}</td>
                        <td>{row_data['Source']}</td>
                    </tr>
"""

    html_content += """                </tbody>
            </table>
            <div class="no-results" id="noResults" style="display: none;">
                No matching records found
            </div>
        </div>

        <div class="footer">
            Report contains potential duplicate assets based on Asset Name, DNS Name, NetBIOS Name, MAC Address, and IPv4 Address
        </div>
    </div>

    <script>
        // Search functionality
        const searchInput = document.getElementById('searchInput');
        const table = document.getElementById('dataTable');
        const tbody = table.querySelector('tbody');
        const noResults = document.getElementById('noResults');
        const resetSortBtn = document.getElementById('resetSortBtn');

        // Store original row order on page load
        const originalRowOrder = Array.from(tbody.querySelectorAll('tr'));

        searchInput.addEventListener('keyup', function() {
            const filter = this.value.toLowerCase();
            const rows = tbody.getElementsByTagName('tr');
            let visibleCount = 0;

            for (let row of rows) {
                const text = row.textContent.toLowerCase();
                if (text.includes(filter)) {
                    row.style.display = '';
                    visibleCount++;
                } else {
                    row.style.display = 'none';
                }
            }

            if (visibleCount === 0) {
                table.style.display = 'none';
                noResults.style.display = 'block';
            } else {
                table.style.display = 'table';
                noResults.style.display = 'none';
            }
        });

        // Sort functionality
        let sortDirections = [true, true, true, true, true];

        function sortTable(columnIndex) {
            const rows = Array.from(tbody.querySelectorAll('tr'));
            const direction = sortDirections[columnIndex];

            rows.sort((a, b) => {
                const aValue = a.cells[columnIndex].textContent.trim();
                const bValue = b.cells[columnIndex].textContent.trim();

                // Try to parse as numbers
                const aNum = parseFloat(aValue);
                const bNum = parseFloat(bValue);

                if (!isNaN(aNum) && !isNaN(bNum)) {
                    return direction ? aNum - bNum : bNum - aNum;
                }

                return direction ?
                    aValue.localeCompare(bValue) :
                    bValue.localeCompare(aValue);
            });

            // Re-append sorted rows
            rows.forEach(row => tbody.appendChild(row));

            // Toggle direction
            sortDirections[columnIndex] = !direction;
        }

        // Column resizing functionality (must be set up BEFORE click handlers)
        const resizers = document.querySelectorAll('.resizer');
        let currentResizer = null;
        let currentTh = null;
        let startX = 0;
        let startWidth = 0;
        let isResizing = false;
        let hasMoved = false;

        resizers.forEach(resizer => {
            resizer.addEventListener('mousedown', function(e) {
                e.stopPropagation();
                e.preventDefault();
                isResizing = true;
                hasMoved = false;
                currentResizer = resizer;
                currentTh = resizer.parentElement;
                startX = e.pageX;
                startWidth = currentTh.offsetWidth;

                document.addEventListener('mousemove', handleMouseMove);
                document.addEventListener('mouseup', handleMouseUp);
            });
        });

        // Add click handlers to table headers for sorting
        const headers = document.querySelectorAll('th[data-column]');
        headers.forEach(th => {
            th.addEventListener('click', function(e) {
                // Don't sort if we just finished resizing
                if (hasMoved) {
                    hasMoved = false;
                    return;
                }
                // Only sort if we didn't click on the resizer
                if (!e.target.classList.contains('resizer')) {
                    const columnIndex = parseInt(this.getAttribute('data-column'));
                    sortTable(columnIndex);
                }
            });
        });

        function handleMouseMove(e) {
            if (currentResizer) {
                hasMoved = true;
                const width = startWidth + (e.pageX - startX);
                if (width > 50) { // Minimum width
                    currentTh.style.width = width + 'px';
                    currentTh.style.minWidth = width + 'px';
                }
            }
        }

        function handleMouseUp() {
            currentResizer = null;
            currentTh = null;
            isResizing = false;
            document.removeEventListener('mousemove', handleMouseMove);
            document.removeEventListener('mouseup', handleMouseUp);

            // Reset hasMoved after a short delay to allow click handler to check it
            setTimeout(() => {
                hasMoved = false;
            }, 10);
        }

        // Reset sort functionality
        resetSortBtn.addEventListener('click', function() {
            // Restore original row order
            originalRowOrder.forEach(row => tbody.appendChild(row));

            // Reset sort directions to initial state
            sortDirections = [true, true, true, true, true];
        });
    </script>
</body>
</html>
"""

    # Write HTML file
    with open(html_filename, 'w', encoding='utf-8') as f:
        f.write(html_content)

    print(f"HTML report exported to {html_filename}\n")
    print(f"File located at {excel_directory}\n")
else:
    print("No duplicates found to export.\n")

# Logout / Invalidate token by posting with token=false
logout_data = {
    "username": username,
    "password": password,
    "token": "false"
}
logout_response = requests.post(auth_url, headers=auth_headers, data=logout_data)
if logout_response.status_code == 200 or logout_response.status_code == 201:
    print("Logout successful.")
else:
    print("Logout may have failed, but token will expire in 4 hours.")
    print(logout_response.text)
