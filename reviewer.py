import json
from openai import OpenAI
from dotenv import load_dotenv
from terraform_reviewer import review_terraform
import argparse

parser = argparse.ArgumentParser()

parser.add_argument(
    "terraform_file",
    help="Terraform file to review"
)

args = parser.parse_args()


with open(args.terraform_file, "r") as f:
    terraform_code = f.read()

review = review_terraform(terraform_code)

for finding in review["findings"]:
    print(finding["title"])
  




