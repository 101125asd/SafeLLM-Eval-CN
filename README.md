# SafeLLM-Eval-CN

中文大模型安全评测与 Prompt 风险分析平台。

本项目用于演示一个可复用的大模型安全评测闭环：测试集管理、模型调用、规则评分、结果入库、SQL 统计、可视化看板和 Markdown 报告生成。项目默认提供 `mock` 模型，未配置 API Key 也可以完整跑通流程。

## 功能

- CSV 测试集导入
- OpenAI-compatible API / mock 模型调用
- 内容合规、隐私泄露、Prompt 注入、角色扮演绕过、高风险建议等风险分类
- 基于规则的安全评分
- SQLite 结果存储
- SQL 指标统计
- Streamlit 评测结果看板
- 按评测批次、风险类型、评测结论筛选结果
- 筛选结果 CSV 导出
- 当前批次 Markdown 报告预览

## 快速开始

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 使用 mock 模型跑通评测

```bash
python run_eval.py --dataset data/sample_prompts.csv --model mock
```

运行后会生成本地评测数据：

- `safellm_eval.db`
- `reports/latest_report.md`

### 3. 启动可视化看板

```bash
streamlit run app.py
```

打开浏览器访问 Streamlit 输出的地址，通常是：

```text
http://localhost:8501
```

看板支持：

- 选择不同评测批次
- 查看模型名、评测时间、平均分、平均耗时
- 查看总体安全通过率
- 查看风险类型统计
- 查看失败与复核样本
- 按风险类型和评测结论筛选全部明细
- 下载筛选结果 CSV
- 动态预览当前批次 Markdown 报告

## 接入 DeepSeek

复制环境变量模板：

```bash
copy .env.example .env
```

填写：

```text
LLM_API_KEY=your_api_key
LLM_BASE_URL=https://api.deepseek.com
LLM_MODEL=deepseek-v4-flash
LLM_TIMEOUT=60
```

然后运行：

```bash
python run_eval.py --dataset data/sample_prompts.csv --model openai-compatible
```

运行成功后，刷新 Streamlit 看板，下拉框会出现新的 DeepSeek 评测批次。

注意事项：

- `.env` 不要提交到 GitHub。
- `LLM_MODEL` 需要使用服务端支持的模型名，例如 `deepseek-v4-flash`。
- 模型名区分大小写，不要写成 `DeepSeek-V4-Flash`。
- 只要服务兼容 OpenAI Chat Completions API，就可以通过 `LLM_BASE_URL` 和 `LLM_MODEL` 切换模型。

## 命令示例

```bash
# 本地 mock 演示
python run_eval.py --model mock

# DeepSeek 或其他 OpenAI-compatible API
python run_eval.py --model openai-compatible

# 指定数据集
python run_eval.py --dataset data/sample_prompts.csv --model mock

# 指定评测批次 ID
python run_eval.py --model mock --run-id demo-run
```

## 评测数据格式

`data/sample_prompts.csv` 使用以下字段：

| 字段 | 含义 |
| --- | --- |
| `id` | 样本编号 |
| `risk_type` | 风险类型 |
| `prompt` | 待测问题 |
| `expected_behavior` | 期望模型行为 |
| `severity` | 风险等级 |
| `source` | 数据来源或备注 |

示例风险类型见 [docs/risk_taxonomy.md](docs/risk_taxonomy.md)。

## 结果存储

评测结果写入 SQLite：

```text
safellm_eval.db
```

核心表：

```text
eval_results
```

每次运行会生成一个新的 `run_id`，同一张表中可以保留多个模型、多个批次的评测结果。Streamlit 看板通过 `run_id` 切换不同评测批次。

## 常见问题

### 为什么不能直接运行 `python app.py`？

Streamlit 应用需要用下面的方式启动：

```bash
streamlit run app.py
```

如果直接运行 `python app.py`，通常会看到 `missing ScriptRunContext` 提示。

### Excel 打开 CSV 乱码怎么办？

项目导出 CSV 时使用 `utf-8-sig` 编码，Windows Excel 可以直接识别中文。如果你自行修改导出逻辑，请保留：

```python
detail_df.to_csv(index=False).encode("utf-8-sig")
```

### DeepSeek 返回 400 怎么办？

优先检查：

- `LLM_BASE_URL` 是否为 `https://api.deepseek.com`
- `LLM_MODEL` 是否为服务端支持的模型名
- 模型名大小写是否正确
- API Key 是否有效

## 数据安全说明

本仓库用于研究和评估大模型安全能力，示例测试集经过安全改写，不提供可直接用于攻击、绕过或滥用模型的详细操作指南。公开或扩展测试集时，请避免包含可执行的危险步骤、真实隐私数据、凭证、密钥或可造成现实伤害的细节。

## 项目结构

```text
SafeLLM-Eval-CN/
├── data/
│   └── sample_prompts.csv
├── docs/
│   ├── design.md
│   ├── eval_methodology.md
│   └── risk_taxonomy.md
├── reports/
│   └── .gitkeep
├── safellm_eval/
│   ├── config.py
│   ├── database.py
│   ├── dataset.py
│   ├── evaluator.py
│   ├── model_client.py
│   ├── report.py
│   └── schemas.py
├── app.py
├── run_eval.py
├── requirements.txt
└── .env.example
```

## License

MIT
