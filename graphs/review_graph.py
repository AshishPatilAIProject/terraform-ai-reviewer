from models.analysis_state import AnalysisState
from langgraph.graph import StateGraph
from services.terraform_parser import parse_terraform
from services.security_checks import run_security_checks
from services.terraform_reviewer import review_terraform
from services.deduplication import deduplicate_findings
from services.risk_scoring import calculate_score
from services.test_generator import generate_tests
from services.remediation_generator import generate_remediation
from services.executive_summary_generator import generate_executive_summary
from services.report_generator import (generate_html_report)
from langgraph.graph import END
import os
from services.agents.security_agent import run_security_agent
from services.agents.compliance_agent import run_compliance_agent
from services.agents.cost_agent import run_cost_agent
from services.compliance_report_generator import generate_compliance_report
from services.cost_report_generator import generate_cost_report

def parse_node(state: AnalysisState):

    state.parsed_terraform = parse_terraform(
        state.terraform_code
    )

    print(
        "Parsed:",
        state.parsed_terraform
    )

    return state

def security_node(state: AnalysisState):

    findings = run_security_checks(
        state.terraform_code,
        state.parsed_terraform
    )

    state.findings.extend(findings)

    print(
        "Security Findings:",
        len(state.findings)
    )

    return state

def review_node(state: AnalysisState):

    findings = review_terraform(
        state.terraform_code
    )

    state.findings.extend(
        findings
    )

    print(
        "Total Findings After AI:",
        len(state.findings)
    )

    return state

def security_agent_node(
    state: AnalysisState
):

    findings = run_security_agent(
        state.terraform_code
    )

    state.findings.extend(
        findings
    )

    print(
        "Security Agent Findings:",
        len(findings)
    )

    return state

def compliance_agent_node(
    state: AnalysisState
):

    findings = run_compliance_agent(
        state.findings
    )

    state.findings.extend(
        findings
    )

    print(
        "Compliance Agent Findings:",
        len(findings)
    )

    return state

def compliance_report_node(
    state: AnalysisState
):

    state.compliance_report = (
        generate_compliance_report(
            state.findings
        )
    )

    print(
        "Generated Compliance Report"
    )

    return state

def cost_report_node(
    state: AnalysisState
):

    state.cost_report = generate_cost_report(
        state.findings
    )

    print(
        "Generated Cost Report"
    )

    return state

def cost_agent_node(
    state: AnalysisState
):

    findings = run_cost_agent(
        state.terraform_code,
        state.parsed_terraform
    )

    state.findings.extend(
        findings
    )

    print(
        "Cost Agent Findings:",
        len(findings)
    )

    return state

def dedup_node(state: AnalysisState):

    before = len(state.findings)

    state.findings = deduplicate_findings(
        state.findings
    )

    after = len(state.findings)

    print(
        f"Deduplicated: {before} -> {after}"
    )

    return state

def score_node(state: AnalysisState):

    for finding in state.findings:
        finding.score = calculate_score(
            finding.severity
        )

    state.total_score = sum(
        finding.score
        for finding in state.findings
    )

    print(
        "Risk Score:",
        state.total_score
    )

    return state

def findings_router(state: AnalysisState):

    if len(state.findings) == 0:
        return "report"

    return "summary"

def test_generation_node(
    state: AnalysisState
):
    state.generated_tests = generate_tests(
        state.terraform_code
    )

    print(
        "Generated Tests"
    )

    return state

def remediation_node(state: AnalysisState):

    state.remediation_plan = generate_remediation(
        state.findings
    )

    print(
        "Generated Remediation Plan"
    )

    return state

def executive_summary_node(state: AnalysisState):

    state.executive_summary = (
        generate_executive_summary(
            state.findings,
            state.total_score
        )
    )

    print(
        "Generated Executive Summary"
    )

    return state

def report_node(state: AnalysisState):

    state.report_html = (
        generate_html_report(
            state
        )
    )

    os.makedirs(
        "reports",
        exist_ok=True
    )

    with open(
        "reports/report.html",
        "w",
        encoding="utf-8"
    ) as f:
        f.write(
            state.report_html
        )

    print(
        "Generated HTML Report"
    )

    return state

def risk_router(
    state: AnalysisState
):

    if state.total_score >= 20:
        print("HIGH RISK PATH")
        return "high_risk"

    print("LOW RISK PATH")
    return "low_risk"

builder = StateGraph(AnalysisState)

builder.add_node(
    "parse",
    parse_node
)

builder.add_node(
    "security",
    security_node
)

builder.add_node(
    "security_agent",
    security_agent_node
)

builder.add_node(
    "compliance_agent",
    compliance_agent_node
)

builder.add_node(
    "compliance_report",
    compliance_report_node
)

builder.add_node(
    "cost_agent",
    cost_agent_node
)

builder.add_node(
    "cost_report",
    cost_report_node
)

builder.add_node(
    "dedup",
    dedup_node
)

builder.add_node(
    "score",
    score_node
)

builder.add_node(
    "generate_tests",
    test_generation_node
)

builder.add_node(
    "remediation",
    remediation_node
)

builder.add_node(
    "executive_summary",
    executive_summary_node
)

builder.add_node(
    "report",
    report_node
)

builder.add_edge(
    "parse",
    "security"
)

builder.add_edge(
    "security",
    "security_agent"
)

builder.add_edge(
    "security_agent",
    "compliance_agent"
)

builder.add_edge(
    "compliance_agent",
    "compliance_report"
)

builder.add_edge(
    "compliance_report",
    "cost_agent"
)

builder.add_edge(
    "cost_agent",
    "cost_report"
)

builder.add_edge(
    "cost_report",
    "dedup"
)

builder.add_edge(
    "dedup",
    "score"
)

builder.add_conditional_edges(
    "score",
    findings_router,
    {
        "summary": "executive_summary",
        "report": "report"
    }
)

builder.add_conditional_edges(
    "executive_summary",
    risk_router,
    {
        "high_risk": "remediation",
        "low_risk": "generate_tests"
    }
)

builder.add_edge(
    "remediation",
    "generate_tests"
)

builder.add_edge(
    "generate_tests",
    "report"
)

builder.set_entry_point(
    "parse"
)
builder.set_finish_point(
    "report"
)
graph = builder.compile()

