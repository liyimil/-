# frontend

课题 D：前端可视化目录。

## 页面结构

- `index.html`：告警事件分析总览
- `workflow.html`：多智能体处理流程
- `events.html`：标准事件中心
- `rules.html`：规则判定结果
- `alarms.html`：结构化告警流
- `assets/app.css`：公共样式
- `assets/app.js`：页面交互与接口请求
- `assets/data.js`：离线兜底数据

## 运行方式

如果本机已经配置 QwenPaw 模型，使用真实 Agent 编排模式：

```bash
python src/web_server/server.py --adapter real --sample-dir data/samples/samples-md --port 8000
```

如果只是本地演示，或尚未配置 QwenPaw 模型，使用离线可运行模式：

```bash
python src/web_server/server.py --adapter demo --sample-dir data/samples/samples-md --port 8000
```

然后打开：

```text
http://127.0.0.1:8000
```

前端会优先读取 `/api/dashboard` 获取最新分析结果；点击“刷新分析”会调用 `/api/run` 重新执行编排流程。若未启动服务，页面会使用 `assets/data.js` 作为离线展示数据。
