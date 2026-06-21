from models.analysis_state import AnalysisState


def generate_html_report(state: AnalysisState) -> str:

    findings_html = ""

    resource_count = len(
    state.parsed_terraform.get(
        "resources",
        []
    )
    )

    workflow_steps = [
    ("Parse", True),
    ("Security Review", True),
    ("AI Review", True),
    ("Risk Scoring", True),
    ("Executive Summary", bool(state.executive_summary)),
    ("Remediation", bool(state.remediation_plan)),
    ("Test Generation", bool(state.generated_tests)),
    ("Report Generation", True)
    ]

    workflow_html = ""

    for step_name, completed in workflow_steps:

        badge_class = (
            "workflow-completed"
            if completed
            else "workflow-skipped"
        )

        badge_icon = (
            "✓"
            if completed
            else "✗"
        )

        workflow_html += f"""
        <div class="{badge_class}">
            {badge_icon} {step_name}
        </div>
        """

    if state.total_score >= 20:
        risk_level = "HIGH"
        risk_class = "risk-high"
    elif state.total_score >= 10:
        risk_level = "MEDIUM"
        risk_class = "risk-medium"
    else:
        risk_level = "LOW"
        risk_class = "risk-low"

    if state.remediation_plan:

        remediation_html = f"""
        <div>
            {state.remediation_plan.replace(chr(10), "<br>")}
        </div>
        """

    else:

        remediation_html = f"""
        <div class="info-box">
            Remediation generation was skipped because the total risk score
            ({state.total_score}) is below the configured threshold (20).

            The workflow generated findings, risk scoring, executive summary,
            Terratest output, and HTML reporting, but did not invoke the
            remediation LLM node.
        </div>
        """

    for finding in state.findings:

        severity_class = (
            "severity-high"
            if finding.severity == "HIGH"
            else "severity-medium"
            if finding.severity == "MEDIUM"
            else "severity-low"
        )

        findings_html += f"""
        <tr>
            <td class="{severity_class}">
                {finding.severity}
            </td>
            <td>{finding.title}</td>
            <td>
    <span class="category-badge">
        {finding.category}
    </span>
</td>
            <td>{finding.score}</td>
        </tr>
        """

    high_count = len(
        [
            f
            for f in state.findings
            if f.severity == "HIGH"
        ]
    )

    medium_count = len(
        [
            f
            for f in state.findings
            if f.severity == "MEDIUM"
        ]
    )

    low_count = len(
        [
            f
            for f in state.findings
            if f.severity == "LOW"
        ]
    )

    html = f"""
<!DOCTYPE html>

<html>

<head>

<title>
Terraform AI Infrastructure Advisor Report
</title>

<style>

body {{
    font-family: "Segoe UI", Arial, sans-serif;
    background: #f5f7fb;
    margin: 0;
    padding: 30px;
}}

.container {{
    max-width: 1400px;
    margin: auto;
}}

.header {{
    background: #1f2937;
    color: white;
    padding: 25px;
    border-radius: 12px;
    margin-bottom: 20px;
}}

.cards {{
    display: flex;
    gap: 20px;
    margin-bottom: 20px;
}}

.card {{
    flex: 1;
    background: white;
    border-radius: 12px;
    padding: 20px;
    box-shadow: 0px 2px 10px rgba(0,0,0,0.08);
}}

.card-title {{
    color: #6b7280;
    font-size: 14px;
}}

.card-value {{
    font-size: 32px;
    font-weight: bold;
    margin-top: 10px;
}}

.section {{
    background: white;
    margin-bottom: 20px;
    padding: 20px;
    border-radius: 12px;
    box-shadow: 0px 2px 10px rgba(0,0,0,0.08);
}}

h1 {{
    margin: 0;
}}

h2 {{
    margin-top: 0;
    color: #111827;
}}

table {{
    width: 100%;
    border-collapse: collapse;
}}

th {{
    background: #111827;
    color: white;
    padding: 12px;
}}

td {{
    padding: 12px;
    border-bottom: 1px solid #e5e7eb;
}}

.severity-high {{
    color: #dc2626;
    font-weight: bold;
}}

.severity-medium {{
    color: #f59e0b;
    font-weight: bold;
}}

.severity-low {{
    color: #10b981;
    font-weight: bold;
}}

pre {{
    white-space: pre-wrap;
    overflow-wrap: break-word;
    background: #f8fafc;
    padding: 15px;
    border-radius: 8px;
    border: 1px solid #e5e7eb;
}}

.risk-badge {{
    display: inline-block;
    padding: 10px 18px;
    border-radius: 8px;
    font-weight: bold;
    font-size: 14px;
    margin-top: 10px;
}}

.risk-high {{
    background: #fee2e2;
    color: #dc2626;
}}

.risk-medium {{
    background: #fef3c7;
    color: #d97706;
}}

.risk-low {{
    background: #dcfce7;
    color: #16a34a;
}}

.category-badge {{
    background: #e5e7eb;
    color: #374151;
    padding: 4px 10px;
    border-radius: 999px;
    font-size: 12px;
    font-weight: 600;
}}

.info-box {{
    background: #eff6ff;
    color: #1e40af;
    border-left: 4px solid #2563eb;
    padding: 15px;
    border-radius: 8px;
}}

.workflow-container {{
    display: flex;
    flex-wrap: wrap;
    gap: 10px;
    margin-top: 15px;
}}

.workflow-completed {{
    background: #dcfce7;
    color: #166534;
    padding: 8px 12px;
    border-radius: 999px;
    font-size: 13px;
    font-weight: 600;
}}

.workflow-skipped {{
    background: #fee2e2;
    color: #b91c1c;
    padding: 8px 12px;
    border-radius: 999px;
    font-size: 13px;
    font-weight: 600;
}}

.footer {{
    margin-top: 30px;
    text-align: center;
    color: #6b7280;
    font-size: 13px;
}}

</style>

</head>

<body>

<div class="container">

<div class="header">

    <h1>
        Terraform AI Infrastructure Advisor
    </h1>

    <div class="risk-badge {risk_class}">
        {risk_level} RISK
    </div>

    <h3>
    Workflow Execution
    </h3>

    <div class="workflow-container">
        {workflow_html}
    </div>
    
</div>

<div class="cards">

    <div class="card">
        <div class="card-title">
            Risk Score
        </div>

        <div class="card-value">
            {state.total_score}
        </div>
    </div>

    <div class="card">
        <div class="card-title">
            High Findings
        </div>

        <div class="card-value">
            {high_count}
        </div>
    </div>

    <div class="card">
        <div class="card-title">
            Medium Findings
        </div>

        <div class="card-value">
            {medium_count}
        </div>
    </div>

    <div class="card">
        <div class="card-title">
            Low Findings
        </div>

        <div class="card-value">
            {low_count}
        </div>
    </div>

    <div class="card">
    <div class="card-title">
        Resources Analyzed
    </div>

    <div class="card-value">
        {resource_count}
    </div>
</div>

</div>

<div class="section">

    <h2>
        Executive Summary
    </h2>

    <div>
    {state.executive_summary.replace(chr(10), "<br>")}
</div>

</div>

<div class="section">

    <h2>
        Findings
    </h2>

    <table>

        <tr>
            <th>Severity</th>
            <th>Title</th>
            <th>Category</th>
            <th>Score</th>
        </tr>

        {findings_html}

    </table>

</div>

<div class="section">

    <h2>
        Remediation Plan
    </h2>

    <div>
    {remediation_html}
</div>

</div>

<div class="section">

    <h2>
        Generated Terratest
    </h2>

    <pre>{state.generated_tests}</pre>

</div>

<div class="footer">
    Generated by Terraform AI Infrastructure Advisor
    <br>
    LangGraph • OpenAI • Terraform
</div>

</div>

</body>
</html>
"""

    return html
