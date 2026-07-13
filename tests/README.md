# tests 目录说明

用于存放测试说明和 golden cases。

第一阶段测试目标：

```text
输入：
data/samples/samples-md/alarms.json
data/samples/samples-md/features.json
data/samples/samples-md/rules.json

期望：
能够读取真实样例数据；
能够解析 ALM-004 这类 signal_name；
能够加载 RULE_0005_LINE_FAULT_REMOTE_CLOSE；
能够解析 rule_id=5 的表达式：
(@1|@2)&@3&(@4|@5|@6)
```
