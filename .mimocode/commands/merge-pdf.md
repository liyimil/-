---
description: "将多个 PDF 文件合并为一个，保留原始文件"
---

# PDF 合并

将指定目录下的多个 PDF 文件合并为一个 PDF。

## 输入

$ARGUMENTS — 包含 PDF 文件的目录路径，可选指定输出文件名和合并顺序

## 工作流程

1. **扫描目录**：列出所有 `.pdf` 文件
2. **检查依赖**：确认 `pypdf` 已安装，未安装则 `pip install pypdf`
3. **排序**：按文件名自然排序（数字章节排序），或按用户指定顺序
4. **合并**：使用 Python 脚本合并

```python
from pypdf import PdfWriter
import os, re

def natural_sort_key(s):
    return [int(c) if c.isdigit() else c.lower() for c in re.split(r'(\d+)', s)]

writer = PdfWriter()
files = sorted([f for f in os.listdir(folder) if f.endswith('.pdf')], key=natural_sort_key)
for f in files:
    writer.append(os.path.join(folder, f))
writer.write(output_path)
```

5. **验证**：检查输出文件页数 = 所有输入文件页数之和

## 输出

- 合并后的 PDF 文件（默认名：`合并.pdf` 或用户指定）
- 原始文件保留不删除
- 报告：合并了多少个文件，总计多少页

## 注意事项

- 使用 `pypdf`（非已废弃的 `PyPDF2`）
- 加密的 PDF 需要密码，跳过并报告
- 大文件合并注意内存使用
