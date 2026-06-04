def run_security_checks(terraform_code: str):
    findings = []
    findings.extend(check_open_ssh(terraform_code))
    findings.extend(check_s3_encryption(terraform_code))
    return findings


def check_open_ssh(terraform_code: str):
    if 'cidr_blocks = ["0.0.0.0/0"]' in terraform_code:
        return [{
            "title": "Open Internet Access Detected",
            "severity": "HIGH",
            "source": "rule-engine"
        }]
    return []

def check_s3_encryption(terraform_code: str):
    if "aws_s3_bucket" in terraform_code:
        if "server_side_encryption_configuration" not in terraform_code:
            return [{
                "title": "S3 Bucket Missing Encryption",
                "severity": "HIGH",
                "source": "rule-engine"
            }]
    return []