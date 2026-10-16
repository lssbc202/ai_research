/* Shared heading navigator for mdBook 0.5.x. Leaves native chapter folding alone. */
(() => {
  "use strict";
  const seen = new WeakSet();
  function enhance() {
    const sidebar = document.querySelector("#mdbook-sidebar, .sidebar");
    if (!sidebar) return;
    // The built-in heading tree may be injected after DOMContentLoaded.
    const lists = sidebar.querySelectorAll("li");
    for (const item of lists) {
      if (seen.has(item)) continue;
      const children = Array.from(item.children);
      const nested = children.find(n => n.tagName === "UL");
      const link = children.find(n => n.tagName === "A");
      // Only page headings (fragment links), not book chapter or month entries.
      if (!nested || !link || !link.getAttribute("href")?.startsWith("#")) continue;
      seen.add(item);
      const btn = document.createElement("button");
      btn.type = "button";
      btn.className = "research-heading-toggle";
      btn.textContent = "▸";
      btn.setAttribute("aria-label", "展开子标题");
      btn.setAttribute("aria-expanded", "false");
      function set(open) {
        nested.hidden = !open;
        btn.textContent = open ? "▾" : "▸";
        btn.setAttribute("aria-expanded", String(open));
        btn.setAttribute("aria-label", open ? "收起子标题" : "展开子标题");
      }
      set(false);
      btn.addEventListener("click", event => {
        event.preventDefault();
        event.stopPropagation();
        set(nested.hidden);
      });
      item.insertBefore(btn, link);
    }
  }
  function start() {
    const sidebar = document.querySelector("#mdbook-sidebar, .sidebar");
    if (!sidebar) return;
    enhance();
    let pending = false;
    const observer = new MutationObserver(() => {
      if (pending) return;
      pending = true;
      requestAnimationFrame(() => { pending = false; enhance(); });
    });
    observer.observe(sidebar, {childList: true, subtree: true});
  }
  if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", start);
  else start();
})();
