# 设计说明

SafeLLM-Eval-CN 的核心流程：

1. 从 CSV 读取安全评测样本。
2. 调用目标模型生成回答。
3. 使用规则评估器判断回答是否安全。
4. 将测试样本、模型回答、耗时、评分和失败原因写入 SQLite。
5. 使用 SQL 聚合指标。
6. 生成 Markdown 报告，并通过 Streamlit 展示结果。

## 模块

- `dataset.py`: 读取和校验测试集。
- `model_client.py`: 模型调用适配层。
- `evaluator.py`: 安全评分逻辑。
- `database.py`: SQLite 表结构和查询。
- `report.py`: Markdown 报告生成。
- `run_eval.py`: CLI 入口。
- `app.py`: 可视化页面。
