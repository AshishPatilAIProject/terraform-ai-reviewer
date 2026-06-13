from dataclasses import dataclass, field
from typing import List
from typing import Dict, Any

from models.finding import Finding

@dataclass
class AnalysisState:
    terraform_code: str

    parsed_terraform: Dict[str, Any] = field(
        default_factory=dict
    )

    findings: List[Finding] = field(
        default_factory=list
    )

    total_score: int = 0

    generated_tests: str = ""