---
name: html2md
description: "批量从 HTML 文件中提取正文内容，去除作者信息和多余标签，转换为干净的 Markdown 文件"
---

# HTML→Markdown 批量提取

从 HTML 文件中提取正文内容，清理后转换为 Markdown 格式。

## 触发条件

用户要求将 HTML 文件（如 CSDN 博客导出）转换为 Markdown。

## 工作流程

### Phase 1: 扫描与分析

1. 扫描目标目录，列出所有 `.html` / `.htm` 文件
2. 读取 2-3 个样本文件，分析 HTML 结构模式
3. 确认：正文容器选择器、标题层级、图片处理方式

### Phase 2: 生成转换脚本

写入 Python 脚本（`convert_html2md.py`），使用 `BeautifulSoup` + `html2text`：

```python
# 核心逻辑
from bs4 import BeautifulSoup
import html2text

def convert(html_path):
    with open(html_path, encoding='utf-8') as f:
        soup = BeautifulSoup(f.read(), 'html.parser')
    
    # 1. 提取正文容器（根据实际结构调整选择器）
    content = soup.select_one('.article_content, .blog_content-box, #content_views')
    
    # 2. 清理：移除 script/style/作者信息/广告
    for tag in content.select('script, style, .blog-tags, .more-toolbox'):
        tag.decompose()
    
    # 3. 转换为 Markdown
    h = html2text.HTML2Text()
    h.body_width = 0  # 不自动换行
    h.protect_links = True
    md = h.handle(str(content))
    
    # 4. 后处理：移除多余空行、修复标题编号
    return clean_markdown(md)
```

### Phase 3: 执行转换

1. 检查依赖：`pip install beautifulsoup4 html2text`
2. 运行脚本，处理所有 HTML 文件
3. 输出到指定目录（默认 `md_output/`）
4. 保留原始目录结构（如按类别分子目录）

### Phase 4: 后处理

- 移除 `<font>` 标签残留
- 清理重复标题（文件名已含标题时去掉正文重复）
- 处理失效图片引用（移除或保留占位符，询问用户）
- 统一 Markdown 格式

## 输出

- 每个 HTML 文件 → 同名 .md 文件
- 转换日志：成功/失败/跳过计数
- 图片统计：移除了多少引用

## 关键注意事项

- Windows 环境下中文路径编码问题：Python 脚本中使用 `sys.stdout.reconfigure(encoding='utf-8')`
- 不同 HTML 源的结构可能不同，先分析样本再调整选择器
- 大批量文件（80+）需要一次性处理，不要一个一个来
