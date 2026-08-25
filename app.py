from pathlib import Path
import pandas as pd
import streamlit as st
from safellm_eval.config import DEFAULT_DB_PATH
from safellm_eval.database import (
    compare_runs,
    connect,
    list_runs,
    load_run_results,
    summarize_run,
)
from safellm_eval.report import build_markdown_report

st.set_page_config(
    page_title="SafeLLM-Eval-CN",
    page_icon="🛡️",
    layout="wide",
)

st.title("SafeLLM-Eval-CN 中文大模型安全评测看板")
st.caption("查看评测批次、总体指标、风险类型统计和失败样本。")

db_path = Path(DEFAULT_DB_PATH)

if not db_path.exists():
    st.warning("还没有找到评测数据库，请先运行：python run_eval.py --model mock")
    st.stop()

connection = connect(db_path)
runs = list_runs(connection)
run_comparison = compare_runs(connection)

if not runs:
    st.warning("数据库中还没有评测记录，请先运行：python run_eval.py --model mock")
    st.stop()

run_options = [row["run_id"] for row in runs]
selected_run_id = st.sidebar.selectbox(
    "选择评测批次",
    run_options,
    format_func=lambda run_id: next(
        f"{row['run_id']} | {row['model_name']} | {row['created_at']}"
        for row in runs
        if row["run_id"] == run_id
    ),
)

selected_run = next(
    row for row in runs if row["run_id"] == selected_run_id
)
st.sidebar.markdown("### 当前批次信息")
st.sidebar.write(f"模型：{selected_run['model_name']}")
st.sidebar.write(f"评测时间：{selected_run['created_at']}")
st.sidebar.write(f"平均分：{selected_run['avg_score']}")
st.sidebar.write(f"平均耗时：{selected_run['avg_latency_ms']} ms")

summary = summarize_run(connection, selected_run_id)
results = load_run_results(connection, selected_run_id)
connection.close()

totals = summary["totals"]
by_risk = summary["by_risk"]
failures = summary["failures"]

total = totals["total"] or 0
safe_count = totals["safe_count"] or 0
unsafe_count = totals["unsafe_count"] or 0
review_count = totals["review_count"] or 0
pass_rate = safe_count / total * 100 if total else 0
st.subheader("评测批次横向对比")

comparison_rows = []
for row in run_comparison:
    comparison_rows.append(
        {
            "评测批次": row["run_id"],
            "模型": row["model_name"],
            "样本数": row["total"],
            "安全通过率": f"{row['pass_rate'] or 0:.1f}%",
            "安全数": row["safe_count"] or 0,
            "不安全数": row["unsafe_count"] or 0,
            "需复核数": row["review_count"] or 0,
            "平均分": row["avg_score"] or 0,
            "平均耗时(ms)": row["avg_latency_ms"] or 0,
            "评测时间": row["created_at"],
        }
    )

st.dataframe(pd.DataFrame(comparison_rows), width="stretch")

st.subheader("当前批次总览")

col1, col2, col3, col4 = st.columns(4)

col1.metric("总样本数", total)
col2.metric("安全通过率", f"{pass_rate:.1f}%")
col3.metric("不安全数", unsafe_count)
col4.metric("需复核数", review_count)

st.subheader("风险类型统计")

risk_row = []
for row in by_risk:
    risk_row.append(
        {
            "风险类型": row["risk_type"],
            "样本数": row["total"],
            "安全数": row["safe_count"] or 0,
            "不安全数": row["unsafe_count"] or 0,
            "需复核数": row["review_count"] or 0,
            "平均分": row["avg_score"] or 0,
        }

)
st.dataframe(risk_row, width="stretch")

st.subheader("失败与复核样本")

if not failures:
    st.success("本次评测没有不安全或需复核样本。")
else:
    failure_rows = []
    for row in failures:
        failure_rows.append(
            {
                "样本编号": row["case_id"],
                "风险类型": row["risk_type"],
                "风险等级": row["severity"],
                "评测结论": row["verdict"],
                "判定原因": row["reason"],
                "Prompt": row["prompt"],
                "模型回答": row["response"],
            }
        )

    st.dataframe(failure_rows, width="stretch")
st.subheader("全部评测明细")

risk_filter_options = ["全部"] + sorted({row["risk_type"] for row in results})
verdict_filter_options = ["全部"] + sorted({row["verdict"] for row in results})
selected_risk_type = st.selectbox("按风险类型筛选", risk_filter_options)
selected_verdict = st.selectbox("按评测结论筛选", verdict_filter_options)

detail_rows = []
for row in results:
    if selected_risk_type != "全部" and row["risk_type"] != selected_risk_type:
        continue

    if selected_verdict != "全部" and row["verdict"] != selected_verdict:
        continue

    detail_rows.append(
        {
            "样本编号": row["case_id"],
            "风险类型": row["risk_type"],
            "模型": row["model_name"],
            "评测结论": row["verdict"],
            "分数": row["score"],
            "耗时(ms)": row["latency_ms"],
            "判定原因": row["reason"],
        }
    )

detail_df = pd.DataFrame(detail_rows)
st.caption(f"当前筛选结果：{len(detail_rows)} 条")
st.dataframe(detail_df, width="stretch")
csv_data = detail_df.to_csv(index=False).encode("utf-8-sig")
st.download_button(
    label="下载筛选结果 CSV",
    data=csv_data,
    file_name=f"{selected_run_id}_filtered_results.csv",
    mime="text/csv",
)
st.subheader("Markdown 报告预览")

report_content = build_markdown_report(selected_run_id, summary)
st.markdown(report_content)
