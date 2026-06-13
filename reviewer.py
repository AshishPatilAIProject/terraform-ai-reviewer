import json
from typing import List
from openai import OpenAI
from dotenv import load_dotenv
from services.terraform_reviewer import review_terraform
import argparse
from services.security_checks import run_security_checks
from services.risk_scoring import calculate_score
from services.deduplication import deduplicate_findings
from models.finding import Finding
import services.test_generator
from models.analysis_state import AnalysisState
from services.terraform_parser import parse_terraform
load_dotenv()

parser = argparse.ArgumentParser()

parser.add_argument(
    "terraform_file",
    help="Terraform file to review"
)

args = parser.parse_args()

with open(args.terraform_file, "r") as f:
    terraform_code = f.read()

state = AnalysisState(
    terraform_code=terraform_code
)

state.parsed_terraform = parse_terraform(
    state.terraform_code
)


state.findings.extend(
    run_security_checks(state.terraform_code, state.parsed_terraform)
)

state.findings.extend(
    review_terraform(state.terraform_code)
)

state.findings = deduplicate_findings(
    state.findings
)

for finding in state.findings:
    finding.score = calculate_score(
        finding.severity
    )

state.total_score = sum(
    finding.score
    for finding in state.findings
)

for finding in state.findings:
    print(
        f"[{finding.severity}] "
        f"{finding.title}"
    )

print("\nTotal Risk Score:", state.total_score)



state.generated_tests = (
    services.test_generator.generate_tests(
        state.terraform_code
    )
)

print("\nGenerated Terratest:")
print("=" * 40 + "\n")
print(state.generated_tests)