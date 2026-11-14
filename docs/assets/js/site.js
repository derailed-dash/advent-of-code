(function () {
  "use strict";

  var THEME_KEY = "aoc-theme";

  function applyTheme(theme) {
    var resolved = theme === "light" ? "light" : "dark";
    document.documentElement.setAttribute("data-theme", resolved);

    var toggleBtn = document.getElementById("theme-toggle");
    var icon = document.getElementById("theme-toggle-icon");
    var label = document.getElementById("theme-toggle-label");
    if (toggleBtn) {
      toggleBtn.setAttribute("aria-pressed", resolved === "light" ? "true" : "false");
      toggleBtn.setAttribute(
        "aria-label",
        resolved === "light" ? "Switch to Midnight Dark theme" : "Switch to Daylight Light theme"
      );
    }
    if (icon) {
      icon.textContent = resolved === "light" ? "\uD83C\uDF19" : "\u2600\uFE0F";
    }
    if (label) {
      label.textContent = resolved === "light" ? "Dark" : "Light";
    }
  }

  function initThemeToggle() {
    var current = document.documentElement.getAttribute("data-theme") || "dark";
    applyTheme(current);

    var toggleBtn = document.getElementById("theme-toggle");
    if (!toggleBtn) return;

    toggleBtn.addEventListener("click", function () {
      var active = document.documentElement.getAttribute("data-theme") || "dark";
      var next = active === "dark" ? "light" : "dark";
      applyTheme(next);
      try {
        localStorage.setItem(THEME_KEY, next);
      } catch (err) {}
    });
  }

  function initDropdown() {
    var dropdown = document.getElementById("years-dropdown");
    if (!dropdown) return;

    document.addEventListener("click", function (event) {
      if (dropdown.open && !dropdown.contains(event.target)) {
        dropdown.open = false;
      }
    });

    document.addEventListener("keydown", function (event) {
      if (event.key === "Escape" && dropdown.open) {
        dropdown.open = false;
      }
    });
  }

  function initDrawer() {
    var shell = document.getElementById("site-shell");
    var openBtn = document.getElementById("sidebar-toggle");
    var closeBtn = document.getElementById("drawer-close");
    var backdrop = document.getElementById("drawer-backdrop");
    var sidebar = document.getElementById("site-sidebar");
    if (!shell || !openBtn || !sidebar) return;

    function setOpen(isOpen) {
      shell.classList.toggle("is-drawer-open", isOpen);
      openBtn.setAttribute("aria-expanded", isOpen ? "true" : "false");
      if (isOpen && closeBtn) {
        closeBtn.focus();
      } else if (!isOpen && document.activeElement && sidebar.contains(document.activeElement)) {
        openBtn.focus();
      }
    }

    openBtn.addEventListener("click", function () {
      setOpen(!shell.classList.contains("is-drawer-open"));
    });

    if (closeBtn) {
      closeBtn.addEventListener("click", function () {
        setOpen(false);
      });
    }

    if (backdrop) {
      backdrop.addEventListener("click", function () {
        setOpen(false);
      });
    }

    sidebar.addEventListener("click", function (event) {
      if (window.innerWidth < 1024 && event.target.closest("a")) {
        setOpen(false);
      }
    });

    document.addEventListener("keydown", function (event) {
      if (event.key === "Escape" && shell.classList.contains("is-drawer-open")) {
        setOpen(false);
      }
    });

    window.addEventListener("resize", function () {
      if (window.innerWidth >= 1024 && shell.classList.contains("is-drawer-open")) {
        shell.classList.remove("is-drawer-open");
        openBtn.setAttribute("aria-expanded", "false");
      }
    });
  }

  function fallbackCopy(text) {
    var area = document.createElement("textarea");
    area.value = text;
    area.setAttribute("readonly", "");
    area.style.position = "fixed";
    area.style.left = "-9999px";
    document.body.appendChild(area);
    area.select();
    try {
      document.execCommand("copy");
    } finally {
      document.body.removeChild(area);
    }
  }

  function copyText(text, onDone) {
    if (navigator.clipboard && navigator.clipboard.writeText) {
      navigator.clipboard.writeText(text).then(onDone).catch(function () {
        fallbackCopy(text);
        onDone();
      });
      return;
    }
    fallbackCopy(text);
    onDone();
  }

  function detectLanguage(container) {
    var match = container.className.match(/language-([a-z0-9_-]+)/i);
    if (match && match[1] && match[1] !== "plaintext") {
      return match[1];
    }
    return "code";
  }

  function initCopyCode() {
    var article = document.getElementById("article-content");
    if (!article) return;

    var blocks = article.querySelectorAll("div.highlighter-rouge, figure.highlight, .prose > pre");
    blocks.forEach(function (block) {
      if (block.parentElement && block.parentElement.closest("div.highlighter-rouge, figure.highlight")) {
        return;
      }

      var container = block;
      var codeElement = block.querySelector("pre code") || block.querySelector("pre");
      if (!codeElement) return;

      if (block.tagName.toLowerCase() === "pre") {
        var wrapper = document.createElement("div");
        wrapper.className = "highlighter-rouge";
        block.parentNode.insertBefore(wrapper, block);
        wrapper.appendChild(block);
        container = wrapper;
      }

      if (container.querySelector(".code-toolbar")) return;

      var toolbar = document.createElement("div");
      toolbar.className = "code-toolbar";

      var langLabel = document.createElement("span");
      langLabel.className = "code-toolbar__lang";
      langLabel.textContent = detectLanguage(container);

      var btn = document.createElement("button");
      btn.type = "button";
      btn.className = "copy-code-btn";
      btn.textContent = "Copy";
      btn.setAttribute("aria-label", "Copy code snippet");

      var resetTimer = null;
      btn.addEventListener("click", function () {
        var text = (codeElement.textContent || "").replace(/\n$/, "");
        copyText(text, function () {
          btn.textContent = "Copied!";
          btn.classList.add("is-copied");
          if (resetTimer) clearTimeout(resetTimer);
          resetTimer = setTimeout(function () {
            btn.textContent = "Copy";
            btn.classList.remove("is-copied");
          }, 1600);
        });
      });

      toolbar.appendChild(langLabel);
      toolbar.appendChild(btn);
      container.insertBefore(toolbar, container.firstChild);
    });
  }

  function slugify(text) {
    return text
      .toLowerCase()
      .trim()
      .replace(/[^a-z0-9\s-]/g, "")
      .replace(/\s+/g, "-")
      .replace(/-+/g, "-");
  }

  function initToc() {
    var shell = document.getElementById("site-shell");
    var article = document.getElementById("article-content");
    var tocAside = document.getElementById("site-toc");
    var tocNav = document.getElementById("toc-nav");
    if (!shell || !article || !tocAside || !tocNav) return;

    var rawHeadings = Array.prototype.slice.call(article.querySelectorAll("h2, h3"));
    var headings = rawHeadings.filter(function (heading) {
      if (heading.id === "page-navigation") return false;
      if (heading.closest(".walkthrough-header") || heading.closest(".not-found-card")) return false;
      return true;
    });

    if (headings.length < 2) {
      tocAside.hidden = true;
      shell.classList.remove("has-toc");
      return;
    }

    var usedIds = {};
    var list = document.createElement("ul");
    list.className = "toc-list";

    var linkById = {};
    headings.forEach(function (heading) {
      if (!heading.id) {
        var baseId = slugify(heading.textContent || "section") || "section";
        var candidate = baseId;
        var suffix = 2;
        while (usedIds[candidate] || document.getElementById(candidate)) {
          candidate = baseId + "-" + suffix;
          suffix += 1;
        }
        heading.id = candidate;
      }
      usedIds[heading.id] = true;

      var listItem = document.createElement("li");
      var link = document.createElement("a");
      link.href = "#" + heading.id;
      link.textContent = heading.textContent.trim();
      link.className = "toc-link" + (heading.tagName.toLowerCase() === "h3" ? " toc-link--h3" : "");
      listItem.appendChild(link);
      list.appendChild(listItem);
      linkById[heading.id] = link;
    });

    tocNav.innerHTML = "";
    tocNav.appendChild(list);
    tocAside.hidden = false;
    shell.classList.add("has-toc");

    function setActiveLink(targetId) {
      Object.keys(linkById).forEach(function (id) {
        linkById[id].classList.toggle("is-active", id === targetId);
      });
    }

    setActiveLink(headings[0].id);

    if ("IntersectionObserver" in window) {
      var observer = new IntersectionObserver(
        function (entries) {
          entries.forEach(function (entry) {
            if (entry.isIntersecting) {
              setActiveLink(entry.target.id);
            }
          });
        },
        { rootMargin: "-76px 0px -70% 0px", threshold: 0 }
      );
      headings.forEach(function (heading) {
        observer.observe(heading);
      });
    }
  }

  document.addEventListener("DOMContentLoaded", function () {
    initThemeToggle();
    initDropdown();
    initDrawer();
    initCopyCode();
    initToc();
  });
})();
