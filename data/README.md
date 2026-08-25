# Data

`sample_prompts.csv` 是安全改写后的示例测试集，用于演示评测流程。

字段说明：

- `id`: 样本编号
- `risk_type`: 风险类型
- `prompt`: 待测问题
- `expected_behavior`: 期望模型行为
- `severity`: 风险等级，`low` / `medium` / `high`
- `source`: 数据来源或备注
