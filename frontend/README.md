# frontend

课题 D：前端可视化目录。

## 页面结构

- `index.html`：总览看板。
- `workflow.html`：A/B/C/D 多智能体编排流程。
- `events.html`：标准事件中心。
- `rules.html`：规则判定与表达式结果。
- `alarms.html`：结构化告警流。
- `assets/app.css`：公共样式。
- `assets/app.js`：公共交互逻辑。
- `assets/data.js`：演示数据。

## 使用方式

直接用浏览器打开：

```text
frontend/index.html
```

当前页面先使用内置 DEMO 数据演示，包含页面跳转、流程节点联动、事件详情展开、规则筛选、告警搜索和跨页面跳转。后续如果接后端接口，可以把 `assets/data.js` 替换成接口返回的 `frontend_data` 映射结果。
