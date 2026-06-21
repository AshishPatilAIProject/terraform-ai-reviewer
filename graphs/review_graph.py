from models.analysis_state import AnalysisState
from langgraph.graph import StateGraph
from services.terraform_parser import parse_terraform
from services.security_checks import run_security_checks
from services.terraform_reviewer import review_terraform
from services.deduplication import deduplicate_findings
from services.risk_scoring import calculate_score
from services.test_generator import generate_tests
from services.remediation_generator import generate_remediation

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
    "review",
    review_node
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

builder.add_edge(
    "parse",
    "security"
)

builder.add_edge(
    "security",
    "review"
)

builder.add_edge(
    "review",
    "dedup"
)

builder.add_edge(
    "dedup",
    "score"
)

builder.add_edge(
    "score",
    "remediation"
)

builder.add_edge(
    "remediation",
    "generate_tests"
)

builder.set_entry_point(
    "parse"
)
builder.set_finish_point(
    "generate_tests"
)
graph = builder.compile()

