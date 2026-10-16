# AI Research Library

公开的 AI 研究笔记、论文综述与专题书籍。每个 `books/<book-id>/` 是一本独立的书。

- 在线：GitHub Pages 上的多本 mdBook。
- 离线：每本书生成 **一份包含全书正文的 HTML**，放在该书网站的 `complete.html`，可以直接发送给别人。
- 扩展：新增书只需创建 `book.toml` 和 `src/` 目录；新增论文只需把 Markdown 放到相应章节目录并推送。
- **章节由你决定**：`src/` 的文件夹即目录章节，文件名按字典序排序（建议 `01-` 等前缀）；Markdown 标题用正文第一个一级标题。

[使用说明](docs/README.md)

首次启用：GitHub 仓库 Settings → Pages → Build and deployment → Source 选择 **GitHub Actions**。推送到 main 后自动构建。
