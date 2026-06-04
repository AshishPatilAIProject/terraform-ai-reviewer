import json
from openai import OpenAI
from dotenv import load_dotenv
from terraform_reviewer import review_terraform
import argparse
from security_checks import check_open_ssh

parser = argparse.ArgumentParser()

parser.add_argument(
    "terraform_file",
    help="Terraform file to review"
)

args = parser.parse_args()

with open(args.terraform_file, "r") as f:
    terraform_code = f.read()

rule_findings = check_open_ssh(terraform_code)
print(rule_findings)

# review = review_terraform(terraform_code)

# for finding in review["findings"]:
#     print(finding["title"])
  




