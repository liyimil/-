# tests 目录说明

用于存放测试说明和 golden cases。

第一阶段测试目标：

```text
同一设备 LINE_01 在 8 秒内出现：
CURRENT_OVER_LIMIT
PROTECTION_ACTION
BREAKER_TRIP

期望：
触发 EVENT_LINE_FAULT
生成线路故障事件
事件等级为高
推送优先级为优先推送
```

