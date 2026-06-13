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

parser = argparse.ArgumentParser()

parser.add_argument(
    "terraform_file",
    help="Terraform file to review"
)

args = parser.parse_args()

with open(args.terraform_file, "r") as f:
    terraform_code = f.read()

rule_findings = run_security_checks(terraform_code)
ai_review = review_terraform(terraform_code)
combined_findings: List[Finding] = []
combined_findings.extend(rule_findings)
combined_findings.extend(ai_review)
for finding in combined_findings:
    finding.score = calculate_score(finding.severity)

combined_findings = deduplicate_findings(combined_findings)

total_score = sum(
    finding.score
    for finding in combined_findings
)


print("\nTerraform Security Review")
print("=" * 40)

for finding in combined_findings:
    print(
        f"[{finding.severity}] "
        f"{finding.title}"
    )

print("\nTotal Risk Score:", total_score)



