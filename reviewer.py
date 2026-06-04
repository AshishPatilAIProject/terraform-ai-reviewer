import json
from openai import OpenAI
from dotenv import load_dotenv
from terraform_reviewer import review_terraform
import argparse
from security_checks import run_security_checks

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
combined_findings = []
combined_findings.extend(rule_findings)
combined_findings.extend(ai_review)
print(combined_findings)


  




