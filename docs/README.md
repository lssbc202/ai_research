# 多书籍构建说明

使用方法与上传规则请优先阅读 [仓库首页 README](../README.md)。

## 目录规则

每本书放在 `books/<book-id>/` 下，包含 `book.toml` 与 `src/`。书籍 ID 决定网站 URL，`book.toml` 的 `[book].title` 决定显示书名。

`src/` 下的目录自动成为章节，`YYYY-MM` 目录显示为“YYYY年M月”。Markdown 文件按文件名排序，正文第一个一级标题作为文章标题。以点号或下划线开头的文件和目录不会被收录，可用 `.gitkeep` 保留暂时没有日报的月份文件夹。

`SUMMARY.md` 在构建时自动生成于临时目录，不提交到 GitHub。**每本书及每个月份都不需要 README.md。** 如果整本书尚未上传日报，构建时会临时生成说明页；空月份不会出现在目录里。

## 自动发布

`main` 分支的书籍内容或构建脚本有提交时，GitHub Actions 自动运行 `python3 scripts/build.py`，安装并使用 mdBook 和 Pandoc，将各书 HTML 发布到 Pages。

- [全部书籍](https://lssbc202.github.io/ai_research/)
- [Agent harness与后训练](https://lssbc202.github.io/ai_research/agent-harness-post-training/)
- [整本单文件 HTML](https://lssbc202.github.io/ai_research/agent-harness-post-training/complete.html)

单文件 HTML 使用 Pandoc 的 `--embed-resources` 和 `--mathml`，可合并各日报离线阅读；在线搜索 JS 不包含在单文件内。

## 可选本地构建

安装 Python 3.11+、mdBook、Pandoc 后，在仓库根目录运行：

```bash
python3 scripts/build.py
```

输出在 `dist/`，构建不修改仓库中的 Markdown。
