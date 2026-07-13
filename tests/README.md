# tests 目录说明

用于存放测试说明和规则用例。

测试目标：

```text
输入：
data/samples/samples-md/alarms.json
data/samples/samples-md/features.json
data/samples/samples-md/rules.json

期望：
能够读取真实样例数据；
能够解析 ALM-004 这类 signal_name；
能够加载 rules.json 中 461 条规则；
能够解析不同形态的 rule.expression；
能够输出规则解析成功/失败统计。
```
