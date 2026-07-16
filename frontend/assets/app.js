(function () {
  const data = window.APP_DATA;
  const page = document.body.dataset.page || "overview";
  const state = {
    selectedModule: "D",
    selectedEventId: data.events[0]?.eventId || "",
    selectedRuleFilter: "all",
    selectedRuleId: "",
    selectedAlarmId: "",
    alarmQuery: ""
  };

  const routes = [
    ["overview", "总览", "index.html"],
    ["workflow", "编排流程", "workflow.html"],
    ["events", "事件中心", "events.html"],
    ["rules", "规则判定", "rules.html"],
    ["alarms", "告警流", "alarms.html"]
  ];

  function $(id) {
    return document.getElementById(id);
  }

  function initFrame() {
    const statusItems = page === "overview"
      ? [
          ["状态", data.status],
          ["Adapter", data.adapterMode]
        ]
      : [
          ["任务", data.taskId],
          ["数据集", data.datasetId],
          ["状态", data.status],
          ["Adapter", data.adapterMode]
        ];

    $("sidebar").innerHTML = `
      <div class="logo">
        <div class="logo-mark">AI</div>
        <div class="logo-title">告警事件分析系统</div>
        <div class="logo-sub">QwenPaw 多智能体编排演示</div>
      </div>
      <nav class="nav">
        ${routes.map(([key, label, href]) => `<a class="${page === key ? "active" : ""}" href="${href}"><span>${label}</span><span>›</span></a>`).join("")}
      </nav>
    `;

    $("topbar").innerHTML = `
      <div>
        <div class="eyebrow">Power Grid Event Intelligence</div>
        <h1>${pageTitle()}</h1>
        <p class="subtitle">${pageSubtitle()}</p>
      </div>
      <div class="status">
        ${statusItems.map(([label, value]) => `<span class="pill">${label} <strong>${value}</strong></span>`).join("")}
      </div>
    `;
  }

  function pageTitle() {
    return {
      overview: "电网告警事件分析看板",
      workflow: "多智能体编排流程",
      events: "标准事件中心",
      rules: "规则判定与表达式结果",
      alarms: "结构化告警流"
    }[page];
  }

  function pageSubtitle() {
    return {
      overview: "展示 A/B/C/D 模块协作链路，将规则触发结果生成标准事件并提供前端可视化。",
      workflow: "按 A -> B -> C -> D 展示 QwenPaw 多智能体编排过程，可点击节点查看模块详情。",
      events: "聚焦 D 模块输出的标准事件，展示事件等级、命中特征、命中告警与生成原因。",
      rules: "展示 C 模块输出的 rule_results，支持触发状态筛选和事件联动。",
      alarms: "展示 A 模块输出的结构化告警，支持搜索并联动到事件证据。"
    }[page];
  }

  function metricCards() {
    return `
      <section class="metrics">
        ${[
          ["输入告警", data.metrics.alarmCount, "来自 A 模块"],
          ["规则判定", data.metrics.ruleResultCount, "来自 C 模块"],
          ["触发事件", data.metrics.triggeredRuleCount, "进入 D 模块"],
          ["标准事件", data.metrics.eventCount, "D 模块输出"]
        ].map(([label, value, note]) => `
          <article class="metric">
            <div class="metric-label">${label}</div>
            <div class="metric-value">${value}</div>
            <div class="metric-note">${note}</div>
          </article>
        `).join("")}
      </section>
    `;
  }

  function renderOverview() {
    const mainEvent = data.events[0];
    $("app").innerHTML = `
      <section class="overview-console">
        <div class="console-copy">
          <div class="eyebrow">System Overview</div>
          <h2 class="hero-title">告警事件主链路已跑通</h2>
          <p class="subtitle">总览页只回答三个问题：系统是否正常、当前识别出什么事件、下一步去哪里看证据。</p>
          <div class="console-stats">
            <div><strong>${data.metrics.alarmCount}</strong><span>输入告警</span></div>
            <div><strong>${data.metrics.ruleResultCount}</strong><span>规则判定</span></div>
            <div><strong>${data.metrics.eventCount}</strong><span>标准事件</span></div>
          </div>
        </div>
        <a class="incident-focus" href="events.html">
          <div class="incident-top">
            <span class="badge danger">${mainEvent.eventLevel}</span>
            <span class="mono">${mainEvent.eventId}</span>
          </div>
          <div class="event-name">${mainEvent.outputText}</div>
          <p class="event-summary">${mainEvent.summary}</p>
          <div class="incident-foot">
            <span>${mainEvent.matchedFeatures.length} 个特征命中</span>
            <span>${mainEvent.matchedAlarms.length} 条告警证据</span>
          </div>
        </a>
      </section>

      <section class="overview-focus">
        <div class="panel flow-panel">
          <div class="panel-head">
            <div>
              <h2 class="panel-title">A/B/C/D 主链路</h2>
              <p class="panel-desc">保留一条最短演示路径，点击节点进入对应详情页。</p>
            </div>
          </div>
          <div class="storyline">
            ${data.workflow.map(item => `
              <a class="story-step ${item.module === "D" ? "active" : ""}" href="${item.module === "A" ? "alarms.html" : item.module === "C" ? "rules.html" : item.module === "D" ? "events.html" : "workflow.html"}">
                <span>${item.module}</span>
                <strong>${item.title}</strong>
                <small>${item.output}</small>
              </a>
            `).join("")}
          </div>
        </div>

        <div class="panel action-panel">
          <div class="panel-head">
            <div>
              <h2 class="panel-title">快速进入</h2>
              <p class="panel-desc">把证据、规则和链路放到二级页，首页保持干净。</p>
            </div>
          </div>
          <div class="action-links">
            <a href="events.html"><strong>事件中心</strong><span>查看 D 输出</span></a>
            <a href="rules.html"><strong>规则判定</strong><span>查看 C 结果</span></a>
            <a href="alarms.html"><strong>告警证据</strong><span>查看 A 输出</span></a>
          </div>
        </div>
      </section>
    `;
  }

  function routeDesc(key) {
    return {
      workflow: "按模块展示智能体输入、输出和执行状态。",
      events: "查看标准事件、命中特征、告警证据。",
      rules: "筛选规则触发结果，定位事件来源。",
      alarms: "检索结构化告警流，查看事件证据。"
    }[key];
  }

  function renderWorkflow() {
    $("app").innerHTML = `
      ${metricCards()}
      <section class="grid-2">
        <div class="panel">
          <div class="panel-head">
            <div>
              <h2 class="panel-title">A/B/C/D 编排链路</h2>
              <p class="panel-desc">点击任意节点，右侧会展示该模块的职责和交付物。</p>
            </div>
            <span class="badge">${data.adapterMode} adapter</span>
          </div>
          <div class="workflow-grid" id="workflowGrid"></div>
        </div>
        <div class="panel">
          <div class="panel-head">
            <div>
              <h2 class="panel-title">模块详情</h2>
              <p class="panel-desc">演示时可以沿着 A -> B -> C -> D 逐个点击讲。</p>
            </div>
          </div>
          <div class="drawer" id="moduleDetail"></div>
        </div>
      </section>
    `;
    renderWorkflowNodes();
    renderModuleDetail();
  }

  function renderWorkflowNodes() {
    $("workflowGrid").innerHTML = data.workflow.map(item => `
      <article class="node ${state.selectedModule === item.module ? "active" : ""}" data-module="${item.module}" tabindex="0">
        <div class="node-mark">${item.module}</div>
        <div class="node-title">${item.title}</div>
        <div class="node-desc">${item.description}</div>
        <div class="node-foot">
          <span class="mono">${item.output}</span>
          <span class="badge ${item.status === "completed" ? "ok" : ""}">${item.status}</span>
        </div>
      </article>
    `).join("");

    document.querySelectorAll("[data-module]").forEach(node => {
      node.addEventListener("click", () => {
        state.selectedModule = node.dataset.module;
        renderWorkflowNodes();
        renderModuleDetail();
      });
    });
  }

  function renderModuleDetail() {
    const item = data.workflow.find(module => module.module === state.selectedModule);
    $("moduleDetail").innerHTML = `
      <div class="detail-card">
        <div class="detail-label">模块</div>
        <div class="detail-value">${item.module} / ${item.name}</div>
      </div>
      <div class="detail-card">
        <div class="detail-label">输入</div>
        <div class="detail-value mono">${item.input}</div>
      </div>
      <div class="detail-card">
        <div class="detail-label">输出</div>
        <div class="detail-value mono">${item.output}</div>
      </div>
      <div class="detail-card">
        <div class="detail-label">职责</div>
        <div class="detail-value">${item.description}</div>
      </div>
    `;
  }

  function renderEventsPage() {
    $("app").innerHTML = `
      <section class="grid-2">
        <div class="panel">
          <div class="panel-head">
            <div>
              <h2 class="panel-title">标准事件列表</h2>
              <p class="panel-desc">点击事件查看命中特征和告警证据。</p>
            </div>
          </div>
          <div class="event-list" id="eventList"></div>
        </div>
        <div class="panel">
          <div class="panel-head">
            <div>
              <h2 class="panel-title">事件详情</h2>
              <p class="panel-desc">D 模块输出的标准事件结构。</p>
            </div>
          </div>
          <div class="drawer" id="eventDetail"></div>
        </div>
      </section>
    `;
    renderEventList();
    renderSelectedEvent();
  }

  function renderEventList() {
    $("eventList").innerHTML = data.events.map(event => eventCard(event, event.eventId === state.selectedEventId)).join("");
    document.querySelectorAll("[data-event-id]").forEach(card => {
      card.addEventListener("click", () => {
        state.selectedEventId = card.dataset.eventId;
        renderEventList();
        renderSelectedEvent();
      });
    });
  }

  function renderSelectedEvent() {
    const event = data.events.find(item => item.eventId === state.selectedEventId);
    $("eventDetail").innerHTML = eventDetails(event);
  }

  function renderRulesPage() {
    $("app").innerHTML = `
      <section class="panel">
        <div class="toolbar">
          <div>
            <h2 class="panel-title">规则判定结果</h2>
            <p class="panel-desc">点击已触发规则可以跳转到对应事件页面。</p>
          </div>
          <div class="segmented" id="ruleFilter">
            <button class="active" data-filter="all">全部</button>
            <button data-filter="hit">已触发</button>
            <button data-filter="miss">未触发</button>
          </div>
        </div>
        <div class="table-wrap">
          <table>
            <thead><tr><th>规则</th><th>表达式</th><th>命中特征</th><th>输出模板</th><th>状态</th></tr></thead>
            <tbody id="ruleRows"></tbody>
          </table>
        </div>
      </section>
    `;
    bindRuleFilter();
    renderRuleRows();
  }

  function bindRuleFilter() {
    $("ruleFilter").addEventListener("click", event => {
      const button = event.target.closest("button");
      if (!button) return;
      state.selectedRuleFilter = button.dataset.filter;
      document.querySelectorAll("#ruleFilter button").forEach(item => item.classList.toggle("active", item === button));
      renderRuleRows();
    });
  }

  function renderRuleRows() {
    const rows = data.rules.filter(rule => {
      if (state.selectedRuleFilter === "hit") return rule.triggered;
      if (state.selectedRuleFilter === "miss") return !rule.triggered;
      return true;
    });

    $("ruleRows").innerHTML = rows.map(rule => `
      <tr class="clickable ${state.selectedRuleId === rule.sourceRuleId ? "selected" : ""}" data-rule-id="${rule.sourceRuleId}">
        <td><strong>${rule.sourceRuleId}</strong><div class="muted">${rule.ruleName}</div></td>
        <td class="mono">${rule.expression}</td>
        <td>${chips(rule.matchedVariables)}</td>
        <td class="mono">${rule.outputFormat}</td>
        <td class="${rule.triggered ? "hit" : "miss"}">${rule.triggered ? "已触发" : "未触发"}</td>
      </tr>
    `).join("");

    document.querySelectorAll("[data-rule-id]").forEach(row => {
      row.addEventListener("click", () => {
        state.selectedRuleId = row.dataset.ruleId;
        const event = data.events.find(item => item.sourceRuleId === state.selectedRuleId);
        if (event) {
          window.location.href = `events.html?event=${event.eventId}`;
        } else {
          renderRuleRows();
        }
      });
    });
  }

  function renderAlarmsPage() {
    $("app").innerHTML = `
      <section class="panel">
        <div class="toolbar">
          <div>
            <h2 class="panel-title">结构化告警流</h2>
            <p class="panel-desc">点击命中告警可以跳转到对应标准事件。</p>
          </div>
          <input class="search" id="alarmSearch" type="search" placeholder="搜索告警 ID、对象或动作">
        </div>
        <div class="table-wrap">
          <table>
            <thead><tr><th>告警 ID</th><th>时间</th><th>厂站</th><th>对象</th><th>动作</th><th>原始告警</th></tr></thead>
            <tbody id="alarmRows"></tbody>
          </table>
        </div>
      </section>
    `;
    $("alarmSearch").addEventListener("input", event => {
      state.alarmQuery = event.target.value;
      renderAlarmRows();
    });
    renderAlarmRows();
  }

  function renderAlarmRows() {
    const query = state.alarmQuery.trim().toLowerCase();
    const rows = data.alarms.filter(alarm => {
      if (!query) return true;
      return [alarm.alarmId, alarm.station, alarm.objectName, alarm.action, alarm.raw]
        .some(value => value.toLowerCase().includes(query));
    });

    $("alarmRows").innerHTML = rows.map(alarm => `
      <tr class="clickable ${state.selectedAlarmId === alarm.alarmId ? "selected" : ""}" data-alarm-id="${alarm.alarmId}">
        <td><strong>${alarm.alarmId}</strong></td>
        <td class="mono">${alarm.time}</td>
        <td>${alarm.station}</td>
        <td>${alarm.objectName}</td>
        <td><span class="badge warn">${alarm.action}</span></td>
        <td>${alarm.raw}</td>
      </tr>
    `).join("");

    document.querySelectorAll("[data-alarm-id]").forEach(row => {
      row.addEventListener("click", () => {
        state.selectedAlarmId = row.dataset.alarmId;
        const event = data.events.find(item => item.matchedAlarms.includes(state.selectedAlarmId));
        if (event) {
          window.location.href = `events.html?event=${event.eventId}`;
        } else {
          renderAlarmRows();
        }
      });
    });
  }

  function eventCard(event, active = false) {
    return `
      <button class="event-card ${active ? "active" : ""}" data-event-id="${event.eventId}">
        <div class="event-top">
          <div>
            <div class="event-id">${event.eventId} / rule_id=${event.sourceRuleId}</div>
            <div class="event-name">${event.outputText}</div>
          </div>
          <div>
            <span class="badge danger">${event.eventLevel}</span>
            <span class="badge">${event.eventType}</span>
          </div>
        </div>
        <p class="event-summary">${event.summary}</p>
      </button>
    `;
  }

  function eventDetails(event) {
    if (!event) return `<div class="detail-card">暂无事件</div>`;
    return `
      <div class="detail-card">
        <div class="detail-label">事件结论</div>
        <div class="detail-value">${event.outputText}</div>
      </div>
      <div class="detail-card">
        <div class="detail-label">触发规则</div>
        <div class="detail-value">${event.ruleName}</div>
        <div class="chips"><span class="chip">rule_id=${event.sourceRuleId}</span></div>
      </div>
      <div class="detail-card">
        <div class="detail-label">命中特征</div>
        <div class="chips">${chips(event.matchedFeatures)}</div>
      </div>
      <div class="detail-card">
        <div class="detail-label">命中告警</div>
        <div class="chips">${chips(event.matchedAlarms)}</div>
      </div>
      <div class="detail-card">
        <div class="detail-label">生成原因</div>
        <div class="detail-value">${event.reason}</div>
      </div>
    `;
  }

  function deliverables() {
    return data.deliverables.map(([flow, payload, path]) => `
      <div class="detail-card">
        <div class="detail-label">${flow}</div>
        <div class="detail-value">${payload}</div>
        <div class="mono muted">${path}</div>
      </div>
    `).join("");
  }

  function chips(values) {
    if (!values || values.length === 0) return `<span class="muted">无</span>`;
    return values.map(value => `<span class="chip">${value}</span>`).join("");
  }

  function applyQueryState() {
    const params = new URLSearchParams(window.location.search);
    const eventId = params.get("event");
    if (eventId && data.events.some(event => event.eventId === eventId)) {
      state.selectedEventId = eventId;
    }
  }

  function init() {
    applyQueryState();
    initFrame();
    if (page === "overview") renderOverview();
    if (page === "workflow") renderWorkflow();
    if (page === "events") renderEventsPage();
    if (page === "rules") renderRulesPage();
    if (page === "alarms") renderAlarmsPage();
  }

  init();
})();
