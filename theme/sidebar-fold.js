/* Shared, self-contained page heading navigator for mdBook 0.5.
   Read headings from the document instead of relying on mdBook's internal sidebar DOM. */
(() => {
  "use strict";
  const start = () => {
    const sidebar = document.querySelector("#mdbook-sidebar .sidebar-scrollbox, #mdbook-sidebar-scrollbox, .sidebar-scrollbox");
    const main = document.querySelector("#content main, .content main, main");
    if (!sidebar || !main || document.getElementById("research-page-toc")) return;
    const headingNodes = Array.from(main.querySelectorAll("h2,h3,h4,h5,h6"))
      .filter(h => h.id && h.textContent.trim());
    if (!headingNodes.length) return;

    const panel = document.createElement("section");
    panel.id = "research-page-toc";
    panel.className = "research-page-toc";
    const header = document.createElement("div");
    header.className = "research-page-toc-header";
    header.textContent = "本篇目录";
    const collapse = document.createElement("button");
    collapse.type = "button";
    collapse.textContent = "全部收起";
    collapse.setAttribute("aria-label", "收起本篇内部目录");
    header.append(collapse);
    panel.append(header);
    const root = document.createElement("ul");
    root.className = "research-toc-list";
    panel.append(root);
    const stack = [{level:1, ul:root}];
    const nodes = [];

    for (const heading of headingNodes) {
      const level = Number(heading.tagName.slice(1));
      while (stack.length > 1 && stack[stack.length-1].level >= level) stack.pop();
      let parent = stack[stack.length-1];
      const item = document.createElement("li");
      item.className = "research-toc-item";
      const link = document.createElement("a");
      link.href = "#" + encodeURIComponent(heading.id);
      link.textContent = heading.textContent.trim();
      item.append(link);
      parent.ul.append(item);
      const ul = document.createElement("ul");
      ul.className = "research-toc-list";
      item.append(ul);
      const node = {item,ul,link,level,button:null};
      nodes.push(node);
      stack.push({level,ul});
    }

    function setOpen(node, open) {
      node.ul.hidden = !open;
      node.button.textContent = open ? "▾" : "▸";
      node.button.setAttribute("aria-expanded", String(open));
      node.button.setAttribute("aria-label", (open ? "收起 " : "展开 ") + node.link.textContent);
    }
    const branchNodes = [];
    for (const node of nodes) {
      if (!node.ul.children.length) {
        node.ul.remove();
        continue;
      }
      const button = document.createElement("button");
      button.type = "button";
      button.className = "research-toc-toggle";
      node.button = button;
      node.item.insertBefore(button, node.link);
      branchNodes.push(node);
      setOpen(node, false);
      button.addEventListener("click", e => {
        e.preventDefault();
        e.stopPropagation();
        setOpen(node, node.ul.hidden);
      });
    }
    // Keep top-level headings visible; deeper sections begin collapsed.
    collapse.addEventListener("click", () => {
      const shouldOpen = branchNodes.every(n => n.ul.hidden);
      branchNodes.forEach(n => setOpen(n, shouldOpen));
      collapse.textContent = shouldOpen ? "全部收起" : "全部展开";
    });
    collapse.textContent = "全部展开";
    sidebar.append(panel);
  };
  if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", start);
  else start();
})();
