from dataclasses import dataclass

@dataclass
class Finding:
    title: str
    category: str
    severity: str
    source: str
    recommendation: str = ""
    score: int = 0
