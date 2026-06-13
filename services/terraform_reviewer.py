from openai import OpenAI
import json
from typing import List
from dotenv import load_dotenv
from models.finding import Finding
from services.normalization import normalize_severity
import os
SECURITY_CHECK_PROMPT_PATH = os.path.join(os.path.dirname(__file__), "..", "prompts", "security_check_ai_prompt.md")

load_dotenv()

client = OpenAI()

def review_terraform(terraform_code: str) -> List[Finding]:

    
    with open(SECURITY_CHECK_PROMPT_PATH, "r") as f:
        prompt = f.read().format(terraform_code=terraform_code)

    response = client.responses.create(
        model="gpt-4.1-mini",
        input=prompt
    )

    raw = response.output_text.strip().removeprefix("```json").removeprefix("```").removesuffix("```").strip()

    findings: List[Finding] = []
    for item in json.loads(raw)["findings"]:
        findings.append(
            Finding(
                title=item["title"],
                category=item["category"],
                severity=normalize_severity(item["severity"]),
                recommendation=item["recommendation"],
                source="llm"
            )
        )
    return findings
