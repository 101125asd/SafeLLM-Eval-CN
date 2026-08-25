from __future__ import annotations

from pathlib import Path


def build_markdown_report(run_id: str, summary: dict[str, object]) -> str:
    totals = summary["totals"]
    by_risk = summary["by_risk"]
    failures = summary["failures"]
    total = totals["total"] or 0
    safe_count = totals["safe_count"] or 0
    pass_rate = safe_count / total * 100 if total else 0

    lines = [
        f"# SafeLLM-Eval-CN 评测报告",
        "",
        f"- Run ID: `{run_id}`",
        f"- 样本数: {total}",
        f"- 安全通过数: {safe_count}",
        f"- 不安全数: {totals['unsafe_count'] or 0}",
        f"- 需复核数: {totals['review_count'] or 0}",
        f"- 安全通过率: {pass_rate:.1f}%",
        f"- 平均分: {totals['avg_score'] or 0}",
        f"- 平均响应耗时: {totals['avg_latency_ms'] or 0} ms",
        "",
        "## 风险类型统计",
        "",
        "| 风险类型 | 样本数 | 安全 | 不安全 | 需复核 | 平均分 |",
        "| --- | ---: | ---: | ---: | ---: | ---: |",
    ]

    for row in by_risk:
        lines.append(
            f"| {row['risk_type']} | {row['total']} | {row['safe_count'] or 0} | "
            f"{row['unsafe_count'] or 0} | {row['review_count'] or 0} | {row['avg_score'] or 0} |"
        )

    lines.extend(["", "## 失败与复核样本", ""])
    if not failures:
        lines.append("本次评测未发现不安全或需复核样本。")
    else:
        for row in failures:
            lines.extend(
                [
                    f"### {row['case_id']} - {row['risk_type']} - {row['verdict']}",
                    "",
                    f"- 风险等级: {row['severity']}",
                    f"- 判定原因: {row['reason']}",
                    f"- Prompt: {row['prompt']}",
                    f"- Response: {row['response']}",
                    "",
                ]
            )

    return "\n".join(lines)


def write_report(path: str | Path, content: str) -> Path:
    report_path = Path(path)
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(content, encoding="utf-8")
    return report_path
