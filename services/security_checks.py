from typing import List
from models.finding import Finding
from typing import Dict, Any
def run_security_checks(terraform_code: str, parsed_terraform: Dict[str, Any]) -> List[Finding]:
    findings: List[Finding] = []
    findings.extend(check_open_ssh(terraform_code))
    findings.extend(check_s3_encryption(terraform_code, parsed_terraform))
    return findings


def check_open_ssh(terraform_code: str) -> List[Finding]:
    if 'cidr_blocks = ["0.0.0.0/0"]' in terraform_code:
        return [
            Finding(
                title="Open Internet Access Detected",
                category="open_ssh",
                severity="HIGH",
                source="rule-engine"
            )
        ]
    return []

def check_s3_encryption(terraform_code: str, parsed_terraform: Dict[str, Any]) -> List[Finding]:
    if "aws_s3_bucket" in parsed_terraform.get("resource_types", []):
        if "server_side_encryption_configuration" not in terraform_code:
            return [
                Finding(
                    title="S3 Bucket Missing Encryption",
                    category="s3_encryption",
                    severity="HIGH",
                    source="rule-engine"
            )
        ]
    return []
