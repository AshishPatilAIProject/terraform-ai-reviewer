def check_open_ssh(terraform_code: str):
    findings = []

    if 'cidr_blocks = ["0.0.0.0/0"]' in terraform_code:
        findings.append({
            "title": "Open Internet Access Detected",
            "severity": "HIGH",
            "source": "rule-engine"
        })

    if "aws_s3_bucket" in terraform_code:
        if "server_side_encryption_configuration" not in terraform_code:
            findings.append({
                "title": "S3 Bucket Missing Encryption",
                "severity": "HIGH",
                "source": "rule-engine"
            })
    return findings

