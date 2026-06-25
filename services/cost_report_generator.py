from openai import OpenAI
from dotenv import load_dotenv
from typing import List
from models.finding import Finding
import os

load_dotenv()

client = OpenAI()

PROMPT_PATH = os.path.join(
    os.path.dirname(__file__),
    "..",
    "prompts",
    "generate_cost_report_prompt.md"
)


def generate_cost_report(
    findings: List[Finding]
) -> str:

    cost_findings = [
        finding
        for finding in findings
        if finding.source == "cost-agent"
    ]

    findings_text = "\n".join(
        [
            (
                f"Title: {finding.title}\n"
                f"Severity: {finding.severity}\n"
                f"Recommendation: {finding.recommendation}\n"
            )
            for finding in cost_findings
        ]
    )

    with open(PROMPT_PATH) as f:
        prompt = f.read().replace(
            "{cost_findings}",
            findings_text
        )

    response = client.responses.create(
        model="gpt-4.1-mini",
        input=prompt
    )

    return response.output_text