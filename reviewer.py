from dotenv import load_dotenv
import argparse
from models.analysis_state import AnalysisState
from graphs.review_graph import graph

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
result = graph.invoke(state)

print(result)

print("\nRemediation Plan")
print("=" * 40)
print(result["remediation_plan"])

