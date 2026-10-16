# 多书籍系统使用说明

## 新建一本书

创建：

```text
books/my-topic/
├── book.toml
└── src/
    ├── README.md
    ├── 01-first-chapter/
    │   ├── 01-paper-one.md
    │   └── 02-paper-two.md
    └── 02-second-chapter/
        └── 01-notes.md
```

`book.toml` 内容：

```toml
[book]
title = "My Topic"
language = "zh"
description = "My research notes"
```

`src/README.md` 是可选首页；各文件夹就是目录中的章节组，按文件夹名称排序。Markdown 的第一个一级标题作为页面标题，文件名是次级排序依据。文件或文件夹以 `_` 或 `.` 开头会被忽略。文件夹可任意嵌套。自动生成的 `SUMMARY.md` 不需要手动维护，亦不要作为内容提交。

本系统根据你设定的目录层级来组织章节，但 mdBook 最终仍然使用自动产生的 `SUMMARY.md`。新增 Markdown 后提交到 main 即触发构建。

## 输出

- 仓库 Pages 首页：`https://lssbc202.github.io/ai_research/`
- 示例书籍：`https://lssbc202.github.io/ai_research/rl-data-synthesis/`
- 整本单文件 HTML：`https://lssbc202.github.io/ai_research/rl-data-synthesis/complete.html`

单 HTML 集中所有文章正文，使用内联 CSS、MathML 数学公式以及嵌入图片以支持离线使用；该文件使用 Pandoc 生成，不是 mdBook 自己的输出。大量文件会使单 HTML 较大。当前单文件版提供浏览器内的章节目录、正文与基础样式；mdBook 的搜索功能仅在在线版提供。

## 本地构建

需安装 Python 3、mdBook、Pandoc：

```bash
python3 scripts/build.py
```

构建结果位于 `dist/`，可在浏览器打开 `dist/index.html`。构建不会修改源码中的 `SUMMARY.md`。

## 设计约定

- 配置发现：`books/*/book.toml`。
- 标题与章节归属由目录及 Markdown 标题决定；不根据创建日期排序。
- 构建时将原始 Markdown 拷贝进临时目录，生成 `SUMMARY.md`，不修改仓库源码。
- 限定所有资源在书籍的 src 下，相对图片路径可正常内嵌。
- 不支持把 mdBook 的搜索 JS 整套嵌入单文件，单文件以全文浏览/浏览器查找为主。
- 用于公开内容，请勿上传未获授权的受版权保护全文或私密数据。
