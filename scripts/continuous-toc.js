(function () {
  "use strict";
  const toc = document.getElementById("TOC");
  if (!toc) return;
  const toolbar = document.createElement("div");
  toolbar.className = "toc-controls";
  const allOpen = document.createElement("button");
  allOpen.type = "button";
  allOpen.textContent = "全部展开";
  const allClose = document.createElement("button");
  allClose.type = "button";
  allClose.textContent = "全部收起";
  toolbar.append(allOpen, allClose);
  toc.prepend(toolbar);
  const entries = [];
  for (const li of toc.querySelectorAll("li")) {
    const children = Array.from(li.children);
    const nested = children.find(child => child.tagName === "UL");
    if (!nested) continue;
    const link = children.find(child => child.tagName === "A");
    const button = document.createElement("button");
    button.type = "button";
    button.className = "toc-toggle";
    li.insertBefore(button, li.firstChild);
    const label = link ? link.textContent.trim() : "子目录";
    function setExpanded(open) {
      nested.hidden = !open;
      button.textContent = open ? "▾" : "▸";
      button.setAttribute("aria-expanded", String(open));
      button.setAttribute("aria-label", (open ? "收起 " : "展开 ") + label);
    }
    // Expand month groups by default; keep individual reports collapsed.
    setExpanded(li.parentElement?.parentElement === toc);
    button.addEventListener("click", () => setExpanded(nested.hidden));
    entries.push({li, setExpanded});
  }
  allOpen.addEventListener("click", () => entries.forEach(entry => entry.setExpanded(true)));
  allClose.addEventListener("click", () => entries.forEach(entry => entry.setExpanded(false)));
})();