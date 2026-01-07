(() => {
  const STORAGE_KEY_VULN = "qcr-widths-vuln-v1";
  const STORAGE_KEY_ASSET = "qcr-widths-asset-v1";
  const STORAGE_KEY_VISIBILITY_VULN = "qcr-visibility-vuln-v1";
  const STORAGE_KEY_VISIBILITY_ASSET = "qcr-visibility-asset-v1";

  // Check if we're on a supported page (opt-in approach - only specific URLs allowed)
  function isSupportedPage() {
    const hash = window.location.hash.split('?')[0];

    // Explicitly excluded paths - never activate on these
    const excludedPaths = [
      '/static-report/prioritization/reports',
      '/static-report/',
      '#/network/trafficAnalyzer',
      '#/network/',
      '#/pm',
      '#/etm'
    ];

    // Check if we're on an excluded path (must match exactly or be a subpath)
    if (excludedPaths.some(path => hash.includes(path))) {
      console.log("[QCR] Page excluded:", hash);
      return false;
    }

    // Only activate on these specific paths
    const allowedPaths = [
      '#/vulnerabilities',
      '#/assets',
      '#/inventory/asset/managed'
    ];

    // Check if the current hash starts with any allowed path
    const isAllowed = allowedPaths.some(path => hash.startsWith(path));
    if (!isAllowed) {
      console.log("[QCR] Page not in allowlist:", hash);
    }
    return isAllowed;
  }

  // Get the appropriate storage key based on current view
  function getStorageKey() {
    const hash = window.location.hash.split('?')[0];
    return (hash.includes('/assets') || hash.includes('/inventory')) ? STORAGE_KEY_ASSET : STORAGE_KEY_VULN;
  }

  // Get the appropriate visibility storage key
  function getVisibilityStorageKey() {
    const hash = window.location.hash.split('?')[0];
    return (hash.includes('/assets') || hash.includes('/inventory')) ? STORAGE_KEY_VISIBILITY_ASSET : STORAGE_KEY_VISIBILITY_VULN;
  }

  // Save column visibility
  function saveColumnVisibility(columnKey, isVisible) {
    const all = loadColumnVisibility();
    all[columnKey] = isVisible;
    localStorage.setItem(getVisibilityStorageKey(), JSON.stringify(all));
    console.log(`[QCR] Saved visibility for ${columnKey}: ${isVisible}`);
  }

  // Load column visibility
  function loadColumnVisibility() {
    try {
      return JSON.parse(localStorage.getItem(getVisibilityStorageKey()) || "{}");
    } catch {
      return {};
    }
  }

  // Apply column visibility
  function applyColumnVisibility() {
    const visibility = loadColumnVisibility();
    const headers = Array.from(document.querySelectorAll('div[role="columnheader"]'));

    headers.forEach((header, index) => {
      const key = (header.textContent || `col-${index}`).trim();
      const isVisible = visibility[key] !== false; // Default to visible

      // Toggle header visibility
      header.style.display = isVisible ? '' : 'none';

      // Toggle body cell visibility
      const allHeaders = Array.from(document.querySelectorAll('div[role="columnheader"]'));
      const idx = allHeaders.indexOf(header);
      if (idx !== -1) {
        const rowGroups = document.querySelectorAll(".rt-tr-group");
        rowGroups.forEach(group => {
          const cells = group.querySelectorAll(".rt-td");
          if (cells[idx]) {
            cells[idx].style.display = isVisible ? '' : 'none';
          }
        });
      }
    });
  }

  // Apply checkbox column sizing for Vulnerability view
  function applyCheckboxColumnSizing() {
    const hash = window.location.hash.split('?')[0];
    if (hash.includes('/vulnerabilities')) {
      const headers = document.querySelectorAll('div[role="columnheader"]');
      if (headers.length > 0 && headers[0].textContent.trim() === "") {
        // First column is checkbox column
        const rowGroups = document.querySelectorAll(".rt-tr-group");
        rowGroups.forEach(group => {
          const firstCell = group.querySelector(".rt-td:first-child");
          if (firstCell) {
            firstCell.style.width = "40px";
            firstCell.style.minWidth = "40px";
            firstCell.style.maxWidth = "40px";
            firstCell.style.flex = "0 0 40px";
          }
        });
      }
    }
  }

  function attachResizers() {
    // Select ALL columnheader elements, not just those with .rt-th
    const headers = document.querySelectorAll('div[role="columnheader"]');
    if (!headers.length) {
      console.log("[QCR] No headers found yet, will retry...");
      return;
    }

    console.log(`[QCR] Found ${headers.length} headers, attaching resizers...`);

    const saved = loadWidths();

    headers.forEach((outerHeader, index) => {
      const inner = outerHeader.querySelector("div:not([role])") || outerHeader;
      const header = inner;
      if (header.dataset.qcrAttached === "true") return;
      header.dataset.qcrAttached = "true";

      const key = (outerHeader.textContent || `col-${index}`).trim();

      outerHeader.style.position = "relative";
      outerHeader.style.overflow = "visible";

      const handle = document.createElement("div");
      handle.className = "qualys-resizer";
      handle.title = "Drag to resize";
      handle.style.pointerEvents = "auto";

      // Make the resizer invisible for empty columns or very narrow columns
      // This includes checkbox columns and other icon-only columns
      if (key.trim() === "" || key.startsWith("col-") || outerHeader.offsetWidth < 60) {
        handle.classList.add("qualys-resizer-hidden");
      }

      handle.addEventListener("mousedown", e => startDrag(e, outerHeader, key));
      outerHeader.appendChild(handle);
    });

    // Apply saved widths after a delay to ensure table is fully rendered
    if (Object.keys(saved).length > 0) {
      setTimeout(() => applySavedWidths(saved), 200);
    }

    // Apply checkbox column sizing for Vulnerability view
    applyCheckboxColumnSizing();

    // Apply column visibility
    applyColumnVisibility();
  }

  // Inject "Columns Shown" into the settings dropdown
  function injectColumnsShownMenu() {
    // Watch for the dropdown menu to appear
    const observer = new MutationObserver(() => {
      const dropdown = document.querySelector('[data-cmp="data-list-page-list-options-menu-layer"]');

      if (dropdown && !dropdown.dataset.qcrColumnsInjected) {
        dropdown.dataset.qcrColumnsInjected = "true";

        const menuWrap = dropdown.querySelector('.menu_menu-wrap-primary_SoN4V');
        if (!menuWrap) return;

        // Get all column headers
        const headers = Array.from(document.querySelectorAll('div[role="columnheader"]'));
        if (!headers.length) return;

        const visibility = loadColumnVisibility();

        // Create "Columns Shown" section with proper wrapper structure matching Rows Shown
        const hoverWrapper = document.createElement('div');
        hoverWrapper.className = 'list-item_wrapper-interactive_kLj8J list-item_wrapper_IZFRj';

        const outerWrapper = document.createElement('div');
        outerWrapper.className = 'list-item_text_j9zIa qx-typography_qx-text-m_tgV62';

        const middleWrapper = document.createElement('span');
        middleWrapper.className = 'list-item_text-wrapper_Px_i4';

        const headerDiv = document.createElement('div');
        headerDiv.className = 'list-item_item-wrapper-interactive_d3iw0 list-item_item-wrapper_sXQqx';
        headerDiv.setAttribute('data-qcr-columns', 'true');
        headerDiv.innerHTML = `<div class="list-item_item-text-icon-both_BvSwr qx-typography_qx-text-m_tgV62">Columns Shown</div><div class="list-item_item-icon-right_IQFPR list-item_item-icon_Y0LbO qx-typography_qx-icon-s_Dj9gv"><div class="qx qx-chevron-right list-item_icon-right_tt_RJ qx-typography_qx-icon-s_Dj9gv qcr-arrow" style="color: rgb(9, 95, 179); transition: transform 0.2s;"></div></div>`;

        const itemsContainer = document.createElement('div');
        itemsContainer.className = 'qcr-columns-items';
        itemsContainer.style.cssText = 'max-height: 0; overflow: hidden; transition: max-height 0.3s ease; background: white; margin-left: 16px;';

        // Build the structure - items container should NOT inherit hover background
        middleWrapper.appendChild(headerDiv);
        outerWrapper.appendChild(middleWrapper);
        hoverWrapper.appendChild(outerWrapper);

        // Toggle expand/collapse on click
        let isExpanded = false;
        const collapseColumns = () => {
          isExpanded = false;
          itemsContainer.style.maxHeight = '0';
          const arrow = headerDiv.querySelector('.qcr-arrow');
          if (arrow) arrow.style.transform = 'rotate(0deg)';
        };

        headerDiv.addEventListener('click', (e) => {
          e.stopPropagation();
          isExpanded = !isExpanded;
          if (isExpanded) {
            itemsContainer.style.maxHeight = '400px';
            const arrow = headerDiv.querySelector('.qcr-arrow');
            if (arrow) arrow.style.transform = 'rotate(90deg)';
          } else {
            collapseColumns();
          }
        });

        // Collapse when clicking anywhere else in the dropdown
        dropdown.addEventListener('click', (e) => {
          if (!hoverWrapper.contains(e.target) && !itemsContainer.contains(e.target)) {
            collapseColumns();
          }
        });

        // Find and attach click listener to "Rows Shown" item to collapse when it's clicked
        // Look for the interactive wrapper that contains "Rows Shown"
        const allMenuItems = Array.from(menuWrap.querySelectorAll('[class*="item-wrapper"]'));
        const rowsShownItem = allMenuItems.find(el => {
          const text = el.textContent.trim();
          return text === 'Rows Shown' || text.startsWith('Rows Shown');
        });

        if (rowsShownItem) {
          console.log('[QCR] Found Rows Shown item, attaching collapse listener');
          rowsShownItem.addEventListener('click', () => {
            console.log('[QCR] Rows Shown clicked, collapsing Columns Shown');
            collapseColumns();
          }, true); // Use capture phase
        } else {
          console.log('[QCR] Warning: Could not find Rows Shown item');
        }

        // Watch for any modal/layer appearing (like Rows Shown modal) and collapse
        const modalObserver = new MutationObserver(() => {
          const modals = document.querySelectorAll('[class*="layer"], [class*="modal"], [class*="popover"]');
          const hasVisibleModal = Array.from(modals).some(modal =>
            modal !== dropdown &&
            modal.offsetParent !== null &&
            (modal.textContent.includes('50') || modal.textContent.includes('100') || modal.textContent.includes('150') || modal.textContent.includes('200'))
          );
          if (hasVisibleModal) {
            collapseColumns();
          }
        });
        modalObserver.observe(document.body, { childList: true, subtree: true });

        // Add checkbox for each column (except first checkbox column)
        headers.forEach((header, index) => {
          const key = (header.textContent || `col-${index}`).trim();

          // Skip empty column (checkbox column) and col-0
          if (key === '' || key.startsWith('col-')) return;

          const isVisible = visibility[key] !== false;

          const item = document.createElement('div');
          item.className = 'qcr-column-item';
          item.style.cssText = 'padding: 8px 12px; cursor: pointer; display: flex; align-items: center; gap: 8px;';

          item.innerHTML = `
            <input type="checkbox"
                   ${isVisible ? 'checked' : ''}
                   data-column-key="${key}"
                   style="cursor: pointer; margin: 0;">
            <span style="flex: 1; user-select: none; font-family: Roboto; font-size: 13px; font-weight: 400; color: rgb(54, 71, 80); line-height: 16px;">${key}</span>
          `;

          // Handle checkbox toggle
          const checkbox = item.querySelector('input[type="checkbox"]');
          item.addEventListener('click', (e) => {
            if (e.target === checkbox) return; // Let checkbox handle itself
            checkbox.checked = !checkbox.checked;
            handleColumnToggle(key, checkbox.checked);
          });

          checkbox.addEventListener('change', (e) => {
            e.stopPropagation();
            handleColumnToggle(key, checkbox.checked);
          });

          itemsContainer.appendChild(item);
        });

        // Insert into menu - header and items as siblings
        menuWrap.appendChild(hoverWrapper);
        menuWrap.appendChild(itemsContainer);

        console.log('[QCR] Injected Columns Shown menu');
      }
    });

    observer.observe(document.body, { childList: true, subtree: true });
  }

  // Handle column visibility toggle
  function handleColumnToggle(columnKey, isVisible) {
    saveColumnVisibility(columnKey, isVisible);
    applyColumnVisibility();
  }

  function applySavedWidths(saved) {
    const headers = document.querySelectorAll('div[role="columnheader"]');
    headers.forEach((outerHeader, index) => {
      const key = (outerHeader.textContent || `col-${index}`).trim();
      if (saved[key]) {
        setColumnWidth(outerHeader, saved[key]);
        updateBodyColumnWidth(outerHeader, parseInt(saved[key]));
      }
    });
    console.log("[QCR] Applied saved column widths");
  }

  function startDrag(e, header, key) {
    e.preventDefault();
    e.stopPropagation();

    const startX = e.clientX;
    const startWidth = header.offsetWidth;

    const onMove = ev => {
      const diff = ev.clientX - startX;
      const newW = Math.max(60, startWidth + diff);
      setColumnWidth(header, newW);
      updateBodyColumnWidth(header, newW);
    };

    const onUp = () => {
      document.removeEventListener("mousemove", onMove, true);
      document.removeEventListener("mouseup", onUp, true);
      saveWidth(key, header.offsetWidth);
    };

    document.addEventListener("mousemove", onMove, true);
    document.addEventListener("mouseup", onUp, true);
  }

  function setColumnWidth(header, width) {
    const widthPx = typeof width === "number" ? `${width}px` : width;
    header.style.width = widthPx;
    header.style.minWidth = widthPx;
    header.style.maxWidth = widthPx;
    header.style.flex = `0 0 ${widthPx}`;
  }

  function updateBodyColumnWidth(header, width) {
    const allHeaders = Array.from(document.querySelectorAll('div[role="columnheader"]'));
    const idx = allHeaders.indexOf(header);
    if (idx === -1) return;

    const widthPx = typeof width === "number" ? `${width}px` : width;

    const rowGroups = document.querySelectorAll(".rt-tr-group");
    rowGroups.forEach(group => {
      const cells = group.querySelectorAll(".rt-td");
      if (cells[idx]) {
        cells[idx].style.width = widthPx;
        cells[idx].style.minWidth = widthPx;
        cells[idx].style.maxWidth = widthPx;
        cells[idx].style.flex = `0 0 ${widthPx}`;
      }
    });
  }

  function saveWidth(key, width) {
    const all = loadWidths();
    all[key] = typeof width === "number" ? `${width}px` : width;
    localStorage.setItem(getStorageKey(), JSON.stringify(all));
    console.log(`[QCR] Saved width for ${key}: ${width}`);
  }

  function loadWidths() {
    try {
      return JSON.parse(localStorage.getItem(getStorageKey()) || "{}");
    } catch {
      return {};
    }
  }

  function startExtension() {
    console.log("[QCR] Column Resizer active on", window.location.hash.split('?')[0]);

    // Persistent observer that watches for table headers appearing/changing
    const observer = new MutationObserver(() => {
      attachResizers();
    });
    observer.observe(document.body, { childList: true, subtree: true });

    // Try to attach resizers immediately
    attachResizers();

    // Progressive retry strategy - more attempts early on, then back off
    const retrySchedule = [100, 300, 500, 800, 1200, 2000, 3000, 5000, 8000];
    retrySchedule.forEach(delay => {
      setTimeout(() => attachResizers(), delay);
    });

    // Inject the column visibility menu
    injectColumnsShownMenu();
  }

  // Track if extension is currently active
  let isActive = false;

  function tryActivate() {
    if (isSupportedPage()) {
      if (!isActive) {
        isActive = true;
        startExtension();
      }
    } else {
      if (isActive) {
        console.log("[QCR] Navigated away from supported page");
        isActive = false;
      }
    }
  }

  // Initial activation attempt
  tryActivate();

  // Listen for hash changes (SPA navigation)
  window.addEventListener('hashchange', () => {
    console.log("[QCR] Hash changed to:", window.location.hash.split('?')[0]);
    tryActivate();
  });

  // Also listen for popstate (browser back/forward)
  window.addEventListener('popstate', () => {
    console.log("[QCR] Popstate event");
    tryActivate();
  });

  // Fallback: periodically check if we're on a supported page
  // This handles cases where hash is set programmatically without events
  setInterval(() => {
    tryActivate();
  }, 1000);
})();
