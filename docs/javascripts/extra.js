// FLEXT Documentation Custom JavaScript

(function () {
  "use strict";

  // Initialize when DOM is ready
  document.addEventListener("DOMContentLoaded", function () {
    initializeProgressBars();
    initializeCodeCopy();
    initializeSearchEnhancement();
    initializeTableSorting();
    initializeVersionBadges();
    initializeMermaidDiagrams();
  });

  // Progress bars for status indicators
  function initializeProgressBars() {
    const progressBars = document.querySelectorAll(".progress-bar");
    progressBars.forEach(function (bar) {
      const fill = bar.querySelector(".progress-fill");
      if (fill) {
        const percentage = fill.getAttribute("data-percentage") || "0";
        fill.style.width = percentage + "%";
      }
    });
  }

  // Enhanced code copy functionality
  function initializeCodeCopy() {
    const codeBlocks = document.querySelectorAll("pre code");
    codeBlocks.forEach(function (block) {
      const button = document.createElement("button");
      button.className = "md-clipboard";
      button.innerHTML =
        '<svg width="16" height="16" viewBox="0 0 24 24"><path fill="currentColor" d="M16 1H4C3 1 2 2 2 3v14h2V3h12V1zm3 4H8C7 5 6 6 6 7v14c0 1 1 2 2 2h11c1 0 2-1 2-2V7c0-1-1-2-2-2zm0 16H8V7h11v14z"/></svg>';
      button.title = "Copy to clipboard";

      button.addEventListener("click", function () {
        const text = block.textContent;
        navigator.clipboard.writeText(text).then(function () {
          button.innerHTML =
            '<svg width="16" height="16" viewBox="0 0 24 24"><path fill="currentColor" d="M9 16.17L4.83 12l-1.42 1.41L9 19 21 7l-1.41-1.41z"/></svg>';
          button.title = "Copied!";
          setTimeout(function () {
            button.innerHTML =
              '<svg width="16" height="16" viewBox="0 0 24 24"><path fill="currentColor" d="M16 1H4C3 1 2 2 2 3v14h2V3h12V1zm3 4H8C7 5 6 6 6 7v14c0 1 1 2 2 2h11c1 0 2-1 2-2V7c0-1-1-2-2-2zm0 16H8V7h11v14z"/></svg>';
            button.title = "Copy to clipboard";
          }, 2000);
        });
      });

      block.parentNode.style.position = "relative";
      block.parentNode.appendChild(button);
    });
  }

  // Enhanced search functionality
  function initializeSearchEnhancement() {
    const searchInput = document.querySelector(".md-search__input");
    if (searchInput) {
      searchInput.addEventListener("input", function () {
        const query = this.value.toLowerCase();
        if (query.length > 2) {
          highlightSearchTerms(query);
        } else {
          removeSearchHighlights();
        }
      });
    }
  }

  // Highlight search terms in content
  function highlightSearchTerms(query) {
    removeSearchHighlights();
    const content = document.querySelector(".md-content");
    if (content) {
      const walker = document.createTreeWalker(
        content,
        NodeFilter.SHOW_TEXT,
        null,
        false,
      );

      const textNodes = [];
      let node;
      while ((node = walker.nextNode())) {
        textNodes.push(node);
      }

      textNodes.forEach(function (textNode) {
        const text = textNode.textContent;
        const regex = new RegExp(`(${query})`, "gi");
        if (regex.test(text)) {
          const highlightedText = text.replace(regex, "<mark>$1</mark>");
          const span = document.createElement("span");
          span.innerHTML = highlightedText;
          textNode.parentNode.replaceChild(span, textNode);
        }
      });
    }
  }

  // Remove search highlights
  function removeSearchHighlights() {
    const marks = document.querySelectorAll("mark");
    marks.forEach(function (mark) {
      const parent = mark.parentNode;
      parent.replaceChild(document.createTextNode(mark.textContent), mark);
      parent.normalize();
    });
  }

  // Table sorting functionality
  function initializeTableSorting() {
    const tables = document.querySelectorAll("table");
    tables.forEach(function (table) {
      const headers = table.querySelectorAll("th");
      headers.forEach(function (header, index) {
        header.style.cursor = "pointer";
        header.addEventListener("click", function () {
          sortTable(table, index);
        });

        // Add sort indicator
        const indicator = document.createElement("span");
        indicator.innerHTML = " ↕";
        indicator.style.fontSize = "0.8em";
        indicator.style.opacity = "0.5";
        header.appendChild(indicator);
      });
    });
  }

  // Sort table by column
  function sortTable(table, columnIndex) {
    const tbody = table.querySelector("tbody");
    const rows = Array.from(tbody.querySelectorAll("tr"));

    rows.sort(function (a, b) {
      const aValue = a.cells[columnIndex].textContent.trim();
      const bValue = b.cells[columnIndex].textContent.trim();

      // Try to parse as number first
      const aNum = parseFloat(aValue);
      const bNum = parseFloat(bValue);

      if (!isNaN(aNum) && !isNaN(bNum)) {
        return aNum - bNum;
      }

      // Fall back to string comparison
      return aValue.localeCompare(bValue);
    });

    // Reorder rows
    rows.forEach(function (row) {
      tbody.appendChild(row);
    });
  }

  // Version badges
  function initializeVersionBadges() {
    const versionElements = document.querySelectorAll("[data-version]");
    versionElements.forEach(function (element) {
      const version = element.getAttribute("data-version");
      const badge = document.createElement("span");
      badge.className = "status-badge";

      if (version.includes("alpha") || version.includes("0.1")) {
        badge.classList.add("status-alpha");
        badge.textContent = "Alpha";
      } else if (version.includes("beta") || version.includes("0.9")) {
        badge.classList.add("status-beta");
        badge.textContent = "Beta";
      } else {
        badge.classList.add("status-stable");
        badge.textContent = "Stable";
      }

      element.appendChild(badge);
    });
  }

  // Mermaid diagram initialization
  function initializeMermaidDiagrams() {
    if (typeof mermaid !== "undefined") {
      mermaid.initialize({
        startOnLoad: true,
        theme: "default",
        flowchart: {
          useMaxWidth: true,
          htmlLabels: true,
        },
        sequence: {
          useMaxWidth: true,
        },
        gantt: {
          useMaxWidth: true,
        },
      });
    }
  }

  // Smooth scrolling for anchor links
  document.querySelectorAll('a[href^="#"]').forEach(function (anchor) {
    anchor.addEventListener("click", function (e) {
      e.preventDefault();
      const target = document.querySelector(this.getAttribute("href"));
      if (target) {
        target.scrollIntoView({
          behavior: "smooth",
          block: "start",
        });
      }
    });
  });

  // Auto-hide header on scroll
  let lastScrollTop = 0;
  window.addEventListener("scroll", function () {
    const header = document.querySelector(".md-header");
    if (header) {
      const scrollTop =
        window.pageYOffset || document.documentElement.scrollTop;
      if (scrollTop > lastScrollTop && scrollTop > 100) {
        header.style.transform = "translateY(-100%)";
      } else {
        header.style.transform = "translateY(0)";
      }
      lastScrollTop = scrollTop;
    }
  });

  // Keyboard shortcuts
  document.addEventListener("keydown", function (e) {
    // Ctrl/Cmd + K for search
    if ((e.ctrlKey || e.metaKey) && e.key === "k") {
      e.preventDefault();
      const searchInput = document.querySelector(".md-search__input");
      if (searchInput) {
        searchInput.focus();
      }
    }

    // Escape to close search
    if (e.key === "Escape") {
      const searchInput = document.querySelector(".md-search__input");
      if (searchInput && document.activeElement === searchInput) {
        searchInput.blur();
      }
    }
  });

  // Print functionality
  function addPrintButton() {
    const printButton = document.createElement("button");
    printButton.innerHTML = "🖨️ Print";
    printButton.className = "md-button md-button--primary";
    printButton.style.position = "fixed";
    printButton.style.bottom = "20px";
    printButton.style.right = "20px";
    printButton.style.zIndex = "1000";

    printButton.addEventListener("click", function () {
      window.print();
    });

    document.body.appendChild(printButton);
  }

  // Initialize print button
  addPrintButton();

  // Analytics tracking
  function trackPageView() {
    if (typeof gtag !== "undefined") {
      gtag("config", "G-XXXXXXXXXX", {
        page_title: document.title,
        page_location: window.location.href,
      });
    }
  }

  // Track page views
  trackPageView();

  // Performance monitoring
  window.addEventListener("load", function () {
    if ("performance" in window) {
      const perfData = performance.getEntriesByType("navigation")[0];
      console.log(
        "Page load time:",
        perfData.loadEventEnd - perfData.loadEventStart,
        "ms",
      );
    }
  });
})();
