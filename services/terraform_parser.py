import re

def parse_terraform(terraform_code: str):
    resources = re.findall(
        r'resource\s+"([^"]+)"\s+"([^"]+)"',
        terraform_code
    )

    return {
    "resources": [
        {
            "type": resource_type,
            "name": resource_name
        }
        for resource_type, resource_name
        in resources
    ]
    }