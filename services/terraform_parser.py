import re

def parse_terraform(terraform_code: str):
    resources = re.findall(
        r'resource\s+"([^"]+)"\s+"([^"]+)"',
        terraform_code
    )

    return {
        "resource_types": [
            resource_type
            for resource_type, _
            in resources
        ]
    }