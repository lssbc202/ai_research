/* Unified mdBook chapter + current page heading navigation. */
(() => {
  "use strict";
  function init() {
    const sidebar = document.querySelector("#mdbook-sidebar .sidebar-scrollbox, #mdbook-sidebar-scrollbox, .sidebar-scrollbox");
    const main = document.querySelector("#content main, .content main, main");
    if (!sidebar || !main || document.querySelector(".research-toc-integrated")) return;
    const chapters = sidebar.querySelector("ol.chapter, .chapter");
    if (!chapters) return;
    // mdBook's index alias can mark the first anchor active even when it is
    // a folder's fold toggle. Only real document links can own a page TOC.
    const pageLinks = Array.from(chapters.querySelectorAll("a[href]"))
      .filter(link => {
        const href = link.getAttribute("href");
        return href && !href.startsWith("#") && !link.classList.contains("chapter-fold-toggle");
      });
    let selected = pageLinks.find(link => link.classList.contains("active"));
    const isBookIndex = typeof path_to_root === "string" && path_to_root === ""
      && /\/(?:index\.html)?$/.test(window.location.pathname);
    if (!selected && isBookIndex) selected = pageLinks[0];
    if (!selected) return;
    const pageLi = selected.closest("li");
    if (!pageLi) return;
    for (const link of chapters.querySelectorAll("a.active")) {
      if (link !== selected) link.classList.remove("active");
    }
    selected.classList.add("active");
    for (let ancestor = pageLi; ancestor && ancestor !== chapters; ancestor = ancestor.parentElement) {
      if (ancestor.classList.contains("chapter-item")) ancestor.classList.add("expanded");
    }
    const headings = Array.from(main.querySelectorAll("h2,h3,h4,h5,h6"))
      .filter(h => h.id && h.textContent.trim());
    if (!headings.length) return;

    const root = document.createElement("ul");
    root.className = "research-toc-list research-toc-integrated";
    const stack = [{level:1, list:root}];
    const branches = [];
    for (const heading of headings) {
      const level = Number(heading.tagName.slice(1));
      while (stack.length > 1 && stack[stack.length-1].level >= level) stack.pop();
      const li = document.createElement("li");
      li.className = "research-toc-item";
      const a = document.createElement("a");
      a.href = "#" + encodeURIComponent(heading.id);
      a.textContent = heading.textContent.trim();
      li.append(a);
      stack[stack.length-1].list.append(li);
      const child = document.createElement("ul");
      child.className = "research-toc-list";
      li.append(child);
      branches.push({li, child, a, button:null});
      stack.push({level, list:child});
    }
    for (const entry of branches) {
      if (!entry.child.childElementCount) {
        entry.child.remove();
        continue;
      }
      const toggle = document.createElement("button");
      toggle.type = "button";
      toggle.className = "research-toc-toggle";
      entry.li.insertBefore(toggle, entry.a);
      entry.button = toggle;
      const setOpen = open => {
        entry.child.hidden = !open;
        toggle.textContent = open ? "▾" : "▸";
        toggle.setAttribute("aria-expanded", String(open));
        toggle.setAttribute("aria-label", (open ? "收起 " : "展开 ") + entry.a.textContent);
      };
      setOpen(false);
      toggle.addEventListener("click", event => {
        event.preventDefault();
        event.stopPropagation();
        setOpen(entry.child.hidden);
      });
    }
    // Append directly inside the current report chapter item, not a separate panel.
    pageLi.append(root);
    pageLi.classList.add("research-current-page");
    // Give the active report its own folding arrow without changing its link.
    const reportButton = document.createElement("button");
    reportButton.type = "button";
    reportButton.className = "research-report-toggle";
    const setReportOpen = open => {
      root.hidden = !open;
      reportButton.textContent = open ? "▾" : "▸";
      reportButton.setAttribute("aria-expanded", String(open));
      reportButton.setAttribute("aria-label", open ? "收起本篇标题" : "展开本篇标题");
    };
    // Newer mdBook versions wrap the document link in chapter-link-wrapper.
    selected.parentElement.insertBefore(reportButton, selected);
    setReportOpen(true);
    reportButton.addEventListener("click", event => {
      event.preventDefault();
      event.stopPropagation();
      setReportOpen(root.hidden);
    });
    // When native mdBook fold is collapsed, the heading navigation follows it.
    const nativeToggle = Array.from(pageLi.children).find(el => el.classList?.contains("chapter-toggle"));
    if (nativeToggle) {
      const observer = new MutationObserver(() => {
        root.hidden = pageLi.classList.contains("chapter-item--collapsed");
      });
      observer.observe(pageLi, {attributes:true,attributeFilter:["class"]});
    }
  }
  if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", init);
  else init();
})();
