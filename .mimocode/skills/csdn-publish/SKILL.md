---
name: csdn-publish
description: "批量将 Markdown 文章通过 Playwright 自动化发布到 CSDN 博客存为草稿"
---

# CSDN 批量发布草稿

通过 Playwright 浏览器自动化，将本地 Markdown 文件批量上传到 CSDN 博客编辑器并保存为草稿。

## 触发条件

用户要求将 Markdown 文件批量上传到 CSDN（或其他类似博客平台）。

## 前置条件

- 用户已登录 CSDN（浏览器有有效 Cookie）
- `playwright` Python 包已安装
- Markdown 文件已准备好

## 工作流程

### Phase 1: 准备

1. 扫描源目录，列出所有 `.md` 文件
2. 读取每个文件的标题（第一个 `# ` 标题）
3. 检查 `playwright` 是否安装，未安装则 `pip install playwright && playwright install chromium`

### Phase 2: 编写自动化脚本

生成 `batch_csdn_draft.py`，核心逻辑：

```python
import asyncio
from playwright.async_api import async_playwright
import markdown

async def publish_one(page, md_content, title):
    # 1. 打开 CSDN 编辑器
    await page.goto('https://mp.csdn.net/mp_blog/creation/editor')
    await page.wait_for_load_state('networkidle')
    
    # 2. 切换到 Markdown 编辑器模式
    # 点击"使用 MD 编辑器"按钮
    md_btn = page.locator('text=使用 MD 编辑器')
    if await md_btn.is_visible():
        await md_btn.click()
        await page.wait_for_timeout(2000)
    
    # 3. 设置标题
    title_input = page.locator('#headTitle input, .input-box input')
    await title_input.fill(title)
    
    # 4. 通过 CKEditor API 设置内容
    # Markdown → HTML 转换
    html_content = markdown.markdown(md_content, extensions=['tables', 'fenced_code'])
    
    # 使用 JS 直接设置编辑器内容
    await page.evaluate(f'''
        const editor = document.querySelector('.cke_wysiwyg_frame, .editor_content');
        if (editor && editor.contentDocument) {{
            editor.contentDocument.body.innerHTML = `{html_content.replace('`', '\\`')}`;
        }}
    ''')
    
    # 5. 保存草稿
    save_btn = page.locator('text=保存草稿, text=Save Draft')
    await save_btn.click()
    await page.wait_for_timeout(3000)

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        context = await browser.new_context(storage_state='csdn_auth.json')
        page = await context.new_page()
        
        for md_file in md_files:
            await publish_one(page, read_file(md_file), extract_title(md_file))
        
        await browser.close()
```

### Phase 3: 执行

1. 首次运行需要用户手动登录并保存认证状态
2. 批量处理所有文件
3. 每篇文章之间加适当延时（3-5秒），避免被限流
4. 记录结果到 `batch_report.json`

### Phase 4: 验证与清理

1. 输出报告：成功/失败/跳过的文章列表
2. 失败的文章记录原因，供重试
3. 清理临时文件（诊断脚本等）

## 关键注意事项

- CSDN 编辑器 DOM 结构可能变化，选择器需要适配
- CKEditor API 方式比模拟键盘输入更可靠
- 图片引用在 CSDN 上会失效，需要告知用户
- 头文件标题（`# title`）与 CSDN 标题栏可能重复，需要去重
- 大批量上传（75+）时注意网络稳定性和限流
- `headless=False` 让用户可以看到进度
- 保存认证状态（`storage_state`）避免重复登录
