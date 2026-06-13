def calculate_score(severity: str) -> int:

    severity = severity.upper()

    mapping = {
        "HIGH": 10,
        "MEDIUM": 5,
        "LOW": 1
    }

    return mapping.get(severity, 0)
