from typing import List
from models.finding import Finding


def deduplicate_findings(findings: List[Finding]) -> List[Finding]:
    seen = set()
    unique: List[Finding] = []

    for finding in findings:

        category = finding.category

        if category not in seen:
            seen.add(category)
            unique.append(finding)

    return unique
