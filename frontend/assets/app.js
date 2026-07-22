(function () {
  let data = window.APP_DATA || emptyData();
  const page = document.body.dataset.page || "overview";
  const state = {
    selectedModule: "D",
    selectedEventId: "",
    selectedRuleFilter: "all",
    selectedRuleId: "",
    selectedAlarmId: "",
    alarmQuery: "",
    apiOnline: false,
    loading: true,
    error: ""
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

  async function loadDashboard() {
    renderLoading();
    try {
      const response = await fetch("/api/dashboard", { cache: "no-store" });
      if (!response.ok) throw new Error(`服务响应 ${response.status}`);
      const payload = await response.json();
      if (payload.status === "error") throw new Error(payload.message || "分析服务暂不可用");
      data = normalizeData(payload);
      state.apiOnline = true;
      state.error = "";
    } catch (error) {
      data = normalizeData(window.APP_DATA || emptyData());
      state.apiOnline = false;
      state.error = `当前展示最近一次分析结果。${error.message}`;
    } finally {
      state.loading = false;
      state.selectedEventId = data.events[0]?.eventId || "";
      applyQueryState();
      render();
    }
  }

  async function runPipeline() {
    const button = $("runPipeline");
    if (button) {
      button.disabled = true;
      button.textContent = "分析中...";
    }
    state.error = "";
    renderNotice("正在刷新告警分析结果，请稍等。");
    try {
      const response = await fetch("/api/run", { method: "POST" });
      if (!response.ok) throw new Error(`服务响应 ${response.status}`);
      const payload = await response.json();
      if (payload.status === "error") throw new Error(payload.message || "分析服务暂不可用");
      data = normalizeData(payload);
      state.apiOnline = true;
      state.selectedEventId = data.events[0]?.eventId || "";
      render();
    } catch (error) {
      state.error = `本次刷新未完成：${error.message}`;
      render();
    } finally {
      const nextButton = $("runPipeline");
      if (nextButton) {
        nextButton.disabled = false;
        nextButton.textContent = "刷新分析";
      }
    }
  }

  function initFrame() {
    const statusItems = page === "overview"
      ? [
          ["状态", displayStatus(data.status)],
          ["编排模式", displayAdapter(data.adapterMode)],
          ["数据源", state.apiOnline ? "实时分析" : "最近结果"]
        ]
      : [
          ["任务", data.taskId || "-"],
          ["数据集", data.datasetId || "-"],
          ["状态", displayStatus(data.status)],
          ["编排模式", displayAdapter(data.adapterMode)]
        ];

    $("sidebar").innerHTML = `
      <div class="logo">
        <div class="logo-mark">AI</div>
        <div class="logo-title">告警事件分析系统</div>
        <div class="logo-sub">多智能体告警识别与事件生成</div>
      </div>
      <nav class="nav">
        ${routes.map(([key, label, href]) => `<a class="${page === key ? "active" : ""}" href="${href}"><span>${label}</span><span>›</span></a>`).join("")}
      </nav>
    `;

    $("topbar").innerHTML = `
      <div>
        <div class="eyebrow">智能告警分析</div>
        <h1>${pageTitle()}</h1>
        <p class="subtitle">${pageSubtitle()}</p>
      </div>
      <div class="top-actions">
        <div class="status">
          ${statusItems.map(([label, value]) => `<span class="pill">${label} <strong>${escapeHtml(value)}</strong></span>`).join("")}
        </div>
        <button class="button primary small" id="runPipeline" type="button">刷新分析</button>
      </div>
    `;

    $("runPipeline").addEventListener("click", runPipeline);
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
      overview: "汇总告警输入、规则判定和事件生成结果，帮助调度人员快速把握当前告警态势。",
      workflow: "展示感知预处理、SKILL 匹配、规则判定与事件生成的处理过程，便于追踪事件来源。",
      events: "聚焦系统识别出的标准事件，展示事件等级、命中特征、告警证据和生成原因。",
      rules: "展示规则判定结果，支持按触发状态筛选，并联动到对应事件。",
      alarms: "展示结构化后的告警流，支持搜索并定位事件证据。"
    }[page];
  }

  function render() {
    initFrame();
    if (state.error) renderNotice(state.error);
    if (page === "overview") renderOverview();
    if (page === "workflow") renderWorkflow();
    if (page === "events") renderEventsPage();
    if (page === "rules") renderRulesPage();
    if (page === "alarms") renderAlarmsPage();
  }

  function renderLoading() {
    $("sidebar").innerHTML = "";
    $("topbar").innerHTML = `
      <div>
        <div class="eyebrow">加载中</div>
        <h1>正在加载告警分析结果</h1>
        <p class="subtitle">系统正在获取最新事件识别结果，请稍等。</p>
      </div>
    `;
    $("app").innerHTML = `<section class="panel"><h2 class="panel-title">正在加载...</h2></section>`;
  }

  function renderNotice(message) {
    const app = $("app");
    if (!app) return;
    const notice = document.createElement("section");
    notice.className = "panel notice";
    notice.innerHTML = `<strong>${escapeHtml(message)}</strong>`;
    app.prepend(notice);
  }

  function metricCards() {
    return `
      <section class="metrics">
        ${[
          ["输入告警", data.metrics.alarmCount, "已完成结构化"],
          ["规则判定", data.metrics.ruleResultCount, "已完成表达式求值"],
          ["触发规则", data.metrics.triggeredRuleCount, "满足事件条件"],
          ["标准事件", data.metrics.eventCount, "已完成事件生成"]
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
    const mainEvent = data.events[0] || {};
    $("app").innerHTML = `
      ${state.error ? `<section class="panel notice"><strong>${escapeHtml(state.error)}</strong></section>` : ""}
      <section class="overview-console">
        <div class="console-copy">
          <div>
            <div class="eyebrow">分析总览</div>
            <h2 class="hero-title">智能告警分析已完成</h2>
            <p class="subtitle">系统已完成告警感知、SKILL 匹配、规则判定与标准事件生成，可在事件中心查看完整证据链。</p>
          </div>
          <div class="console-stats">
            <div><strong>${data.metrics.alarmCount}</strong><span>输入告警</span></div>
            <div><strong>${data.metrics.ruleResultCount}</strong><span>规则判定</span></div>
            <div><strong>${data.metrics.eventCount}</strong><span>标准事件</span></div>
          </div>
        </div>
        <a class="incident-focus" href="events.html">
          <div class="incident-top">
            <span class="badge danger">${escapeHtml(mainEvent.eventLevel || "未触发事件")}</span>
            <span class="mono">${escapeHtml(mainEvent.eventId || "-")}</span>
          </div>
          <div class="event-name">${escapeHtml(mainEvent.outputText || "当前未识别到标准事件")}</div>
          <p class="event-summary">${escapeHtml(mainEvent.summary || "当前告警未满足已配置事件规则。")}</p>
          <div class="incident-foot">
            <span>${(mainEvent.matchedFeatures || []).length} 个特征命中</span>
            <span>${(mainEvent.matchedAlarms || []).length} 条告警证据</span>
          </div>
        </a>
      </section>

      <section class="overview-focus">
        <div class="panel flow-panel">
          <div class="panel-head">
            <div>
              <h2 class="panel-title">事件识别流程</h2>
              <p class="panel-desc">从告警解析到事件生成，展示各模块的处理结果和上下游关系。</p>
            </div>
          </div>
          <div class="storyline">
            ${data.workflow.map(item => `
              <a class="story-step ${item.module === "D" ? "active" : ""}" href="${moduleHref(item.module)}">
                <span>${escapeHtml(item.module)}</span>
                <strong>${escapeHtml(item.title)}</strong>
                <small>${escapeHtml(item.output)}</small>
              </a>
            `).join("")}
          </div>
        </div>

        <div class="panel action-panel">
          <div class="panel-head">
            <div>
              <h2 class="panel-title">快速查看</h2>
              <p class="panel-desc">按事件、规则和告警三个视角查看分析结果。</p>
            </div>
          </div>
          <div class="action-links">
            <a href="events.html"><strong>事件中心</strong><span>查看标准事件</span></a>
            <a href="rules.html"><strong>规则判定</strong><span>查看命中依据</span></a>
            <a href="alarms.html"><strong>告警证据</strong><span>查看结构化告警</span></a>
          </div>
        </div>
      </section>
    `;
  }

  function renderWorkflow() {
    $("app").innerHTML = `
      ${state.error ? `<section class="panel notice"><strong>${escapeHtml(state.error)}</strong></section>` : ""}
      ${metricCards()}
      <section class="grid-2">
        <div class="panel">
          <div class="panel-head">
            <div>
              <h2 class="panel-title">多智能体处理流程</h2>
              <p class="panel-desc">选择任一节点，右侧展示该模块的职责、输入输出和处理数量。</p>
            </div>
            <span class="badge">${escapeHtml(displayAdapter(data.adapterMode))}</span>
          </div>
          <div class="workflow-grid" id="workflowGrid"></div>
        </div>
        <div class="panel">
          <div class="panel-head">
            <div>
              <h2 class="panel-title">环节详情</h2>
              <p class="panel-desc">用于说明事件从告警输入到标准化输出的完整路径。</p>
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
      <article class="node ${state.selectedModule === item.module ? "active" : ""}" data-module="${escapeHtml(item.module)}" tabindex="0">
        <div class="node-mark">${escapeHtml(item.module)}</div>
        <div class="node-title">${escapeHtml(item.title)}</div>
        <div class="node-desc">${escapeHtml(item.description)}</div>
        <div class="node-foot">
          <span class="mono">${escapeHtml(item.output)}</span>
          <span class="badge ${item.status === "completed" ? "ok" : ""}">${escapeHtml(item.status)}</span>
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
    const item = data.workflow.find(module => module.module === state.selectedModule) || data.workflow[0] || {};
    $("moduleDetail").innerHTML = `
      <div class="detail-card"><div class="detail-label">处理环节</div><div class="detail-value">${escapeHtml(item.module)} / ${escapeHtml(item.title || item.name)}</div></div>
      <div class="detail-card"><div class="detail-label">接收内容</div><div class="detail-value mono">${escapeHtml(item.input)}</div></div>
      <div class="detail-card"><div class="detail-label">生成结果</div><div class="detail-value mono">${escapeHtml(item.output)}</div></div>
      <div class="detail-card"><div class="detail-label">职责</div><div class="detail-value">${escapeHtml(item.description)}</div></div>
      <div class="detail-card"><div class="detail-label">本次处理数量</div><div class="detail-value">${escapeHtml(item.count || 0)}</div></div>
    `;
  }

  function renderEventsPage() {
    $("app").innerHTML = `
      ${state.error ? `<section class="panel notice"><strong>${escapeHtml(state.error)}</strong></section>` : ""}
      <section class="grid-2">
        <div class="panel">
          <div class="panel-head"><div><h2 class="panel-title">标准事件列表</h2><p class="panel-desc">选择事件查看命中特征和告警证据。</p></div></div>
          <div class="event-list" id="eventList"></div>
        </div>
        <div class="panel">
          <div class="panel-head"><div><h2 class="panel-title">事件详情</h2><p class="panel-desc">系统生成的标准事件识别结果。</p></div></div>
          <div class="drawer" id="eventDetail"></div>
        </div>
      </section>
    `;
    renderEventList();
    renderSelectedEvent();
  }

  function renderEventList() {
    $("eventList").innerHTML = data.events.map(event => eventCard(event, event.eventId === state.selectedEventId)).join("") || `<div class="detail-card">暂无事件</div>`;
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
      ${state.error ? `<section class="panel notice"><strong>${escapeHtml(state.error)}</strong></section>` : ""}
      <section class="panel">
        <div class="toolbar">
          <div>
            <h2 class="panel-title">规则判定结果</h2>
            <p class="panel-desc">已触发规则可关联到对应标准事件。</p>
          </div>
          <div class="segmented" id="ruleFilter">
            <button class="active" data-filter="all">全部</button>
            <button data-filter="hit">已触发</button>
            <button data-filter="miss">未触发</button>
          </div>
        </div>
        <div class="table-wrap">
          <table>
            <thead><tr><th>规则</th><th>表达式</th><th>命中特征</th><th>事件描述模板</th><th>状态</th></tr></thead>
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
      <tr class="clickable ${state.selectedRuleId === rule.sourceRuleId ? "selected" : ""}" data-rule-id="${escapeHtml(rule.sourceRuleId)}">
        <td><strong>${escapeHtml(rule.sourceRuleId)}</strong><div class="muted">${escapeHtml(rule.ruleName)}</div></td>
        <td class="mono">${escapeHtml(rule.expression)}</td>
        <td>${chips(rule.matchedVariables)}</td>
        <td class="mono">${escapeHtml(rule.outputFormat)}</td>
        <td class="${rule.triggered ? "hit" : "miss"}">${rule.triggered ? "已触发" : "未触发"}</td>
      </tr>
    `).join("");

    document.querySelectorAll("[data-rule-id]").forEach(row => {
      row.addEventListener("click", () => {
        state.selectedRuleId = row.dataset.ruleId;
        const event = data.events.find(item => item.sourceRuleId === state.selectedRuleId);
        if (event) window.location.href = `events.html?event=${encodeURIComponent(event.eventId)}`;
        else renderRuleRows();
      });
    });
  }

  function renderAlarmsPage() {
    $("app").innerHTML = `
      ${state.error ? `<section class="panel notice"><strong>${escapeHtml(state.error)}</strong></section>` : ""}
      <section class="panel">
        <div class="toolbar">
          <div>
            <h2 class="panel-title">结构化告警流</h2>
            <p class="panel-desc">命中告警可关联到对应标准事件。</p>
          </div>
          <input class="search" id="alarmSearch" type="search" placeholder="搜索告警 ID、厂站、对象或动作">
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
        .some(value => String(value || "").toLowerCase().includes(query));
    });

    $("alarmRows").innerHTML = rows.map(alarm => `
      <tr class="clickable ${state.selectedAlarmId === alarm.alarmId ? "selected" : ""}" data-alarm-id="${escapeHtml(alarm.alarmId)}">
        <td><strong>${escapeHtml(alarm.alarmId)}</strong></td>
        <td class="mono">${escapeHtml(alarm.time)}</td>
        <td>${escapeHtml(alarm.station)}</td>
        <td>${escapeHtml(alarm.objectName)}</td>
        <td><span class="badge warn">${escapeHtml(alarm.action)}</span></td>
        <td>${escapeHtml(alarm.raw)}</td>
      </tr>
    `).join("");

    document.querySelectorAll("[data-alarm-id]").forEach(row => {
      row.addEventListener("click", () => {
        state.selectedAlarmId = row.dataset.alarmId;
        const event = data.events.find(item => item.matchedAlarms.includes(state.selectedAlarmId));
        if (event) window.location.href = `events.html?event=${encodeURIComponent(event.eventId)}`;
        else renderAlarmRows();
      });
    });
  }

  function eventCard(event, active = false) {
    return `
      <button class="event-card ${active ? "active" : ""}" data-event-id="${escapeHtml(event.eventId)}">
        <div class="event-top">
          <div>
            <div class="event-id">${escapeHtml(event.eventId)} / rule_id=${escapeHtml(event.sourceRuleId)}</div>
            <div class="event-name">${escapeHtml(event.outputText)}</div>
          </div>
          <div>
            <span class="badge danger">${escapeHtml(event.eventLevel)}</span>
            <span class="badge">${escapeHtml(event.eventType)}</span>
          </div>
        </div>
        <p class="event-summary">${escapeHtml(event.summary)}</p>
      </button>
    `;
  }

  function eventDetails(event) {
    if (!event) return `<div class="detail-card">暂无事件</div>`;
    return `
      <div class="detail-card"><div class="detail-label">事件结论</div><div class="detail-value">${escapeHtml(event.outputText)}</div></div>
      <div class="detail-card"><div class="detail-label">触发规则</div><div class="detail-value">${escapeHtml(event.ruleName)}</div><div class="chips"><span class="chip">rule_id=${escapeHtml(event.sourceRuleId)}</span></div></div>
      <div class="detail-card"><div class="detail-label">命中特征</div><div class="chips">${chips(event.matchedFeatures)}</div></div>
      <div class="detail-card"><div class="detail-label">命中告警</div><div class="chips">${chips(event.matchedAlarms)}</div></div>
      <div class="detail-card"><div class="detail-label">生成原因</div><div class="detail-value">${escapeHtml(event.reason)}</div></div>
    `;
  }

  function chips(values) {
    if (!values || values.length === 0) return `<span class="muted">无</span>`;
    return values.map(value => `<span class="chip">${escapeHtml(value)}</span>`).join("");
  }

  function moduleHref(module) {
    return module === "A" ? "alarms.html" : module === "C" ? "rules.html" : module === "D" ? "events.html" : "workflow.html";
  }

  function displayStatus(status) {
    return {
      completed: "分析完成",
      running: "分析中",
      error: "需关注",
      empty: "暂无结果"
    }[status] || status || "-";
  }

  function displayAdapter(adapter) {
    return {
      real: "QwenPaw 编排",
      demo: "本地流程",
      mock: "离线样例"
    }[adapter] || adapter || "-";
  }

  function applyQueryState() {
    const params = new URLSearchParams(window.location.search);
    const eventId = params.get("event");
    if (eventId && data.events.some(event => event.eventId === eventId)) state.selectedEventId = eventId;
  }

  function normalizeData(payload) {
    const normalized = payload || {};
    normalized.metrics = normalized.metrics || {};
    normalized.workflow = normalized.workflow || [];
    normalized.events = normalized.events || [];
    normalized.rules = normalized.rules || [];
    normalized.alarms = normalized.alarms || [];
    normalized.deliverables = normalized.deliverables || [];
    normalized.metrics.alarmCount = normalized.metrics.alarmCount || normalized.alarms.length;
    normalized.metrics.ruleResultCount = normalized.metrics.ruleResultCount || normalized.rules.length;
    normalized.metrics.triggeredRuleCount = normalized.metrics.triggeredRuleCount || normalized.rules.filter(rule => rule.triggered).length;
    normalized.metrics.eventCount = normalized.metrics.eventCount || normalized.events.length;
    return normalized;
  }

  function emptyData() {
    return {
      taskId: "",
      datasetId: "",
      status: "empty",
      adapterMode: "",
      metrics: {},
      workflow: [],
      events: [],
      rules: [],
      alarms: [],
      deliverables: []
    };
  }

  function escapeHtml(value) {
    return String(value ?? "")
      .replace(/&/g, "&amp;")
      .replace(/</g, "&lt;")
      .replace(/>/g, "&gt;")
      .replace(/"/g, "&quot;")
      .replace(/'/g, "&#039;");
  }

  loadDashboard();
})();
