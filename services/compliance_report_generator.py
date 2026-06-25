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
    "generate_compliance_report_prompt.md"
)

def generate_compliance_report(
    findings: List[Finding]
) -> str:

    compliance_findings = [
        finding
        for finding in findings
        if finding.source == "compliance-agent"
    ]

    findings_text = "\n".join(
        [
            (
                f"Title: {finding.title}\n"
                f"Severity: {finding.severity}\n"
                f"{finding.recommendation}\n"
            )
            for finding in compliance_findings
        ]
    )

    with open(
        PROMPT_PATH,
        "r"
    ) as f:

        prompt = f.read().replace(
            "{compliance_findings}",
            findings_text
        )

    response = client.responses.create(
        model="gpt-4.1-mini",
        input=prompt
    )

    return response.output_text