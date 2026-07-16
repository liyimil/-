window.APP_DATA = {
  taskId: "TASK-MOCK-0001",
  datasetId: "demo-dataset",
  status: "completed",
  adapterMode: "demo",
  metrics: {
    alarmCount: 3,
    ruleResultCount: 2,
    triggeredRuleCount: 1,
    eventCount: 1
  },
  workflow: [
    {
      module: "A",
      name: "perception_agent",
      title: "感知预处理",
      input: "raw_alarms",
      output: "structured_alarms",
      status: "completed",
      count: 3,
      description: "解析原始告警文本，抽取时间、厂站、对象和动作。"
    },
    {
      module: "B",
      name: "skill_engine",
      title: "SKILL 匹配",
      input: "structured_alarms",
      output: "skill_match",
      status: "completed",
      count: 1,
      description: "加载 Feature/Rule SKILL，并生成 signal_mapping_states。"
    },
    {
      module: "C",
      name: "expression_engine",
      title: "表达式求值",
      input: "skill_match",
      output: "expression_result",
      status: "completed",
      count: 2,
      description: "求值 feature.expression 与 rule.expression，输出 rule_results。"
    },
    {
      module: "D",
      name: "event_generator",
      title: "事件生成",
      input: "expression_result",
      output: "events",
      status: "completed",
      count: 1,
      description: "将触发规则转换为标准事件，并组织前端展示数据。"
    }
  ],
  events: [
    {
      eventId: "EVT-0001",
      sourceRuleId: "5",
      ruleName: "[精准]20kV线路故障（远方手合）",
      eventType: "2-跳闸事件",
      eventLevel: "事故",
      outputText: "演示变电站一号线路 线路故障（远方手合）",
      matchedAlarms: ["DEMO-ALM-001", "DEMO-ALM-002", "DEMO-ALM-003"],
      matchedFeatures: ["@1", "@3", "@4", "@5"],
      reason: "特征 @1、@3、@4、@5 为 true，规则表达式整体求值为 true。",
      summary: "系统根据规则“[精准]20kV线路故障（远方手合）”识别出2-跳闸事件。"
    }
  ],
  rules: [
    {
      sourceRuleId: "5",
      ruleName: "[精准]20kV线路故障（远方手合）",
      expression: "(@1|@2)&@3&(@4|@5|@6)",
      triggered: true,
      matchedVariables: ["@1", "@3", "@4", "@5"],
      unmatchedVariables: ["@2", "@6"],
      eventType: "2-跳闸事件",
      eventLevel: "事故",
      outputFormat: "$LINE 线路故障（远方手合）",
      matchedAlarms: ["DEMO-ALM-001", "DEMO-ALM-002", "DEMO-ALM-003"]
    },
    {
      sourceRuleId: "902",
      ruleName: "[基础]开关合上",
      expression: "(@6)",
      triggered: false,
      matchedVariables: [],
      unmatchedVariables: ["@6"],
      eventType: "6-一般告知",
      eventLevel: "告知",
      outputFormat: "$BAY 开关投入运行",
      matchedAlarms: []
    }
  ],
  alarms: [
    {
      alarmId: "DEMO-ALM-001",
      time: "2026-07-13 09:00:01",
      station: "演示变电站",
      objectName: "一号线路保护",
      action: "A网中断",
      raw: "2026年07月13日 09:00:01 演示变电站 一号线路保护A网中断 动作"
    },
    {
      alarmId: "DEMO-ALM-002",
      time: "2026-07-13 09:00:05",
      station: "演示变电站",
      objectName: "演示开关01",
      action: "分闸",
      raw: "2026年07月13日 09:00:05 演示变电站 演示开关01 分闸"
    },
    {
      alarmId: "DEMO-ALM-003",
      time: "2026-07-13 09:02:10",
      station: "演示变电站",
      objectName: "演示开关01",
      action: "合闸",
      raw: "2026年07月13日 09:02:10 演示变电站 演示开关01 合闸"
    }
  ],
  deliverables: [
    ["A -> B", "structured_alarms", "data/generated/structured_alarms.json"],
    ["B -> C", "skill_match", "data/generated/skill_match.json"],
    ["C -> D", "expression_result", "data/generated/expression_result.json"],
    ["D -> 前端/报告", "orchestration_result / events", "data/generated/orchestration_result.json"]
  ]
};
