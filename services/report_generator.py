import markdown

from models.analysis_state import AnalysisState


def generate_html_report(state: AnalysisState) -> str:

    findings_html = ""
    compliance_html = ""
    compliance_report_html = ""
    cost_html = ""
    resources_html = ""
    cost_report_html = ""

    resource_count = len(
    state.parsed_terraform.get(
        "resources",
        []
    )
    )

    compliance_count = len([
        f for f in state.findings
        if f.source == "compliance-agent"
    ])

    cost_count = len([
        f for f in state.findings
        if f.source == "cost-agent"
    ])

    workflow_steps = [
        ("Parse", True),
        ("Security Agent", True),
        ("Compliance Agent", compliance_count > 0),
        ("Cost Agent", cost_count > 0),
        ("Risk Scoring", True),
        ("Executive Summary", bool(state.executive_summary)),
        ("Remediation", bool(state.remediation_plan)),
        ("Test Generation", bool(state.generated_tests)),
        ("Report Generation", True)
        ]

    security_count = len([
    f for f in state.findings
        if f.source in ["rule-engine", "llm"]
        ])

    compliance_findings = [
    f for f in state.findings
    if f.source == "compliance-agent"
    ]

    cost_findings = [
    f for f in state.findings
    if f.source == "cost-agent"
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

    for resource in state.parsed_terraform.get(
    "resources",
    []
    ):

        resources_html += f"""
        <tr>
            <td>{resource["type"]}</td>
            <td>{resource["name"]}</td>
        </tr>
        """
    for finding in compliance_findings:

        severity_class = (
            "severity-high"
            if finding.severity == "HIGH"
            else "severity-medium"
            if finding.severity == "MEDIUM"
            else "severity-low"
        )

        compliance_html += f"""
        <tr>
            <td>{finding.title}</td>

            <td class="{severity_class}">
                {finding.severity}
            </td>

            <td>
                {finding.recommendation}
            </td>
        </tr>
        """

    compliance_report_html = f"""
        <div class="section ai-card">

            <div style="
                display:flex;
                justify-content:space-between;
                align-items:center;
                margin-bottom:15px;
            ">

                <h2 style="margin:0;">
                    🧠 AI Compliance Advisor
                </h2>

                <span class="ai-badge">
                    AI Generated
                </span>

            </div>

            <div class="markdown">
                {markdown.markdown(state.compliance_report)}
            </div>

            <hr style="
                margin-top:20px;
                border:none;
                border-top:1px solid #dbeafe;
            ">

            <div class="ai-note">
                Generated using deterministic compliance mappings combined with
                LLM-based explanations. No additional compliance findings were
                created.
            </div>

        </div>
        """

    for finding in cost_findings:

        severity_class = (
            "severity-high"
            if finding.severity == "HIGH"
            else "severity-medium"
            if finding.severity == "MEDIUM"
            else "severity-low"
        )

        cost_html += f"""
        <tr>
            <td>
                {finding.title}
            </td>

            <td class="{severity_class}">
                {finding.severity}
            </td>

            <td>
                {finding.recommendation}
            </td>
        </tr>
        """

    cost_report_html = f"""
        <div class="section ai-card">

        <div style="
            display:flex;
            justify-content:space-between;
            align-items:center;
            margin-bottom:15px;
        ">

        <h2 style="margin:0;">
            💰 AI Cost Advisor
        </h2>

        <span class="ai-badge">
            AI Generated
        </span>

        </div>

        <div class="markdown">
            {markdown.markdown(state.cost_report)}
        </div>

        <hr style="
            margin-top:20px;
            border:none;
            border-top:1px solid #dbeafe;
        ">

        <div class="ai-note">
            Generated using deterministic cost optimization findings combined
            with LLM-based recommendations. No additional cost findings were
            created.
        </div>
    </div>
    """

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

.ai-card{{
    background:#f6fbff;
    border-left:5px solid #2563eb;
    padding:20px;
    border-radius:10px;
    margin-bottom:20px;
}}

.ai-badge{{
    background:#2563eb;
    color:white;
    padding:6px 12px;
    border-radius:999px;
    font-size:12px;
    font-weight:bold;
}}

.ai-note{{
    margin-top:15px;
    padding:12px;
    background:#eff6ff;
    border-left:4px solid #2563eb;
    font-size:13px;
    color:#1e3a8a;
    border-radius:8px;
}}

    .markdown h1,
    .markdown h2,
    .markdown h3{{
    margin-top:20px;
    color:#111827;
}}

    .markdown ul{{
        padding-left:22px;
}}

    .markdown li{{
        margin-bottom:8px;
}}

    .markdown p{{
        line-height:1.7;
}}

    .markdown code{{
        background:#eef2ff;
        padding:2px 5px;
        border-radius:4px;
        font-family:Consolas, monospace;
}}

    .markdown pre{{
        background:#0f172a;
        color:#f8fafc;
        padding:15px;
        border-radius:8px;
        overflow-x:auto;
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
</div>

<div class="cards">

    <div class="card">
        <div class="card-title">
            Security Agent
        </div>

        <div class="card-value">
            {security_count}
        </div>
    </div>

    <div class="card">
        <div class="card-title">
            Compliance Agent
        </div>

        <div class="card-value">
            {compliance_count}
        </div>
    </div>

    <div class="card">
        <div class="card-title">
            Cost Agent
        </div>

        <div class="card-value">
            {cost_count}
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
    Infrastructure Inventory
    </h2>

    <table>

    <tr>
        <th>Resource Type</th>
        <th>Name</th>
    </tr>

    {resources_html}

    </table>

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
    Compliance Impact
    </h2>

    <table>

    <tr>
        <th>Framework</th>
        <th>Severity</th>
        <th>Controls</th>
    </tr>

    {compliance_html}

    </table>
</div>

{compliance_report_html}

<div class="section">
    <h2>
    Cost Optimization Opportunities
    </h2>

    <table>

    <tr>
        <th>Finding</th>
        <th>Severity</th>
        <th>Recommendation</th>
    </tr>

    {cost_html}

    </table>

</div>

{cost_report_html}

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
