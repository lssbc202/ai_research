# AI Research Library

本仓库用于公开发布 AI 领域的论文调研与分析日报，将持续积累的 Markdown 按专题整理成独立书籍，以便连续阅读、搜索、跨论文分析和分享。

**当前书籍：** [Agent harness与后训练](https://lssbc202.github.io/ai_research/agent-harness-post-training/) · [整本书 HTML](https://lssbc202.github.io/ai_research/agent-harness-post-training/complete.html)

## 上传日报

在对应书籍的月份文件夹中提交 Markdown 文件，不要上传到仓库根目录。示例结构（日报文件仅为举例）：

```text
books/
└── agent-harness-post-training/
    ├── book.toml
    └── src/
        ├── 2026-10/
        │   ├── 2026-10-16.md
        │   └── 2026-10-17.md
        └── 2026-11/
            └── 2026-11-01.md
```

上传规范：

1. **月份目录**使用 `YYYY-MM` 格式，例如 `2026-10`；每个月一个目录，从 2026 年 10 月开始。
2. **日报文件**使用 `YYYY-MM-DD.md` 格式，日期应与所在月份一致；同一天推荐维护一篇日报。
3. **Markdown** 使用 UTF-8 编码，以清晰的一级标题 `# 日报标题` 开头，二级和三级标题用于组织内容。一级标题会作为书籍导航中的文章名。
4. **研究内容**应有论文名称、原文链接和必要引用，清楚区分论文结论与个人分析。不要上传个人隐私、凭证或无权公开的受版权保护内容。
5. **图片与公式**：图片可放到月份目录下的 `images/`，使用相对路径引用；公式用标准 LaTeX 语法。尽量避免依赖远程加载的图片，方便单文件 HTML 离线分享。
6. **命名兼容性**：路径推荐英文、数字、短横线，避免空格、`#`、`?`、括号等特殊符号。文章的显示标题可以使用中文和标点。

可以通过 GitHub 网页的 **Add file → Upload files / Create new file** 上传，也可以本地 `git push` 至 `main`。提交后 GitHub Actions 自动构建和发布，**不需要手动生成 SUMMARY.md，也不需要本地安装 mdBook**。空月份暂不显示，首次放入日报后自动出现。

## 新增一本书

在 `books/<book-id>/` 新建 `book.toml` 和 `src/` 目录，示例：

```toml
[book]
title = "书籍名称"
description = "书籍简介"
language = "zh"
src = "src"

[output.html]
mathjax-support = true
```

随后创建章节目录并放入 Markdown 即可。**目录即章节**，目录和文件按名称排序；需要时用数字前缀决定顺序。每本书有自己的配置与内容，但共用一套构建脚本和 GitHub Actions。新书无内容时自动生成临时空书说明，不需要专门编写占位文件。

## 生成与阅读

- [多书籍首页](https://lssbc202.github.io/ai_research/)：所有书籍入口。
- **在线版**：mdBook 支持章节目录、翻页和全文搜索。
- **整本单 HTML**：每本书的 `complete.html` 汇总所有文章，便于离线连续阅读与分享；外链资源不保证离线可用。
- **本地构建（可选）**：安装 Python 3.11+、mdBook、Pandoc 后，在仓库根目录执行 `python3 scripts/build.py`，结果输出到不纳入版本管理的 `dist/`。

有关构建和发布的技术说明请参阅 [docs/README.md](docs/README.md)。
