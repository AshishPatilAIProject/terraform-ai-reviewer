# Terraform AI Reviewer

Terraform AI Reviewer is an AI-assisted Infrastructure-as-Code (IaC) analysis platform built using Python, OpenAI APIs, Terraform, and LangGraph.

The project combines deterministic security checks with LLM-powered Terraform reviews to identify infrastructure risks, calculate risk scores, remove duplicate findings, and generate Terratest test cases.

The workflow is orchestrated using LangGraph, with a shared AnalysisState flowing through multiple analysis nodes.

---

## Features

### Terraform Parsing

Parses Terraform files and extracts infrastructure resource metadata.

Example:

```terraform
resource "aws_s3_bucket" "example" {
  bucket = "my-demo-bucket"
}
```

Parsed output:

```json
{
  "resources": [
    {
      "type": "aws_s3_bucket",
      "name": "example"
    }
  ]
}
```

---

### Rule-Based Security Checks

Deterministic security checks identify common Terraform misconfigurations.

Current checks:

* Open SSH access (`0.0.0.0/0`)
* Missing S3 bucket encryption

Example finding:

```text
[HIGH] Open Internet Access Detected
```

---

### AI-Powered Terraform Review

Uses OpenAI models to identify additional security issues such as:

* Missing versioning
* Missing public access block configuration
* Security best practice violations
* Infrastructure recommendations

---

### Finding Normalization

Normalizes AI output into a consistent internal format.

Example:

```text
high
HIGH
High
```

becomes:

```text
HIGH
```

---

### Finding Categorization

All findings are mapped into categories such as:

```text
open_ssh
s3_encryption
s3_versioning
s3_public_access
```

This allows findings from multiple analysis engines to be compared consistently.

---

### Deduplication Engine

Removes duplicate findings produced by both:

* Rule Engine
* AI Reviewer

Example:

```text
Rule Engine:
S3 Bucket Missing Encryption

AI:
S3 Bucket Without Server-Side Encryption
```

Both are categorized as:

```text
s3_encryption
```

Only one finding is retained.

---

### Risk Scoring

Findings are assigned severity scores.

| Severity | Score |
| -------- | ----- |
| HIGH     | 10    |
| MEDIUM   | 5     |
| LOW      | 1     |

Example:

```text
HIGH + MEDIUM + HIGH

10 + 5 + 10

Total Risk Score = 25
```

---

### Terratest Generation

Generates starter Terratest code from Terraform configurations.

Example output:

```go
func TestTerraformModule(t *testing.T) {
    terraform.InitAndApply(t, terraformOptions)
}
```

### LangGraph Workflow Orchestration

Coordinates analysis stages using a shared AnalysisState and LangGraph nodes.

---

## LangGraph Workflow
```text
AnalysisState
      |
      v
Terraform Parser
      |
      v
Rule Engine
      |
      +------------------+
      |                  |
      v                  v
Security Checks     AI Reviewer
      |                  |
      +--------+---------+
               |
               v
      Deduplication
               |
               v
        Risk Scoring
               |
               v
      Terratest Generator
               |
               v
        Updated AnalysisState
```

---
## Shared Workflow State

The application uses a shared AnalysisState object that flows through all LangGraph nodes.

```python
@dataclass
class AnalysisState:
    terraform_code: str
    parsed_terraform: Dict[str, Any]
    findings: List[Finding]
    total_score: int
    generated_tests: str
```

Each node reads from and updates the state, allowing analysis stages to remain loosely coupled.
---

## Project Structure

```text
terraform-ai-reviewer/

├── reviewer.py
│
├── graphs/
│   └── review_graph.py
│
├── prompts/
│   ├── security_check_ai_prompt.md
│   └── generate_test_prompt.md
│
├── models/
│   ├── finding.py
│   └── analysis_state.py
│
├── services/
│   ├── terraform_parser.py
│   ├── terraform_reviewer.py
│   ├── security_checks.py
│   ├── deduplication.py
│   ├── risk_scoring.py
│   ├── normalization.py
│   └── test_generator.py
│
├── sample1.tf
├── sample2.tf
└── README.md
```

---

## Installation

### Clone Repository

```bash
git clone https://github.com/AshishPatilAIProject/terraform-ai-reviewer.git

cd terraform-ai-reviewer
```

### Create Virtual Environment

```bash
python -m venv venv
```

Activate:

Windows:

```bash
venv\Scripts\activate
```

Linux / Mac:

```bash
source venv/bin/activate
```

### Install Dependencies

```bash
pip install openai python-dotenv
```

### Configure Environment

Create:

```text
.env
```

```env
OPENAI_API_KEY=your_api_key_here
```

---

## Usage

Review Terraform:

```bash
python reviewer.py sample1.tf
```

Example output:

```text
Parsed: {'resources': [{'type': 'aws_security_group', 'name': 'web'}]}
Security Findings: 1
Total Findings After AI: 2
Deduplicated: 2 -> 1
[HIGH] Open Internet Access Detected

Total Risk Score: 10

Generated Terratest:
========================================
```go
package test

import (
        "testing"
        "os"
        "path/filepath"

        "github.com/gruntwork-io/terratest/modules/terraform"
)

func TestTerraformModule(t *testing.T) {
        t.Parallel()

        // Construct the path to the Terraform code folder
        terraformDir := filepath.FromSlash("../path/to/terraform/code")

        // Terraform options
        terraformOptions := &terraform.Options{
                TerraformDir: terraformDir,

                // Variables to pass to Terraform
                Vars: map[string]interface{}{},
        }

        // Clean up resources with "terraform destroy" at the end of the test
        defer terraform.Destroy(t, terraformOptions)

        // Initialize and apply Terraform code
        terraform.InitAndApply(t, terraformOptions)

        // Optionally, add validations/assertions for your Terraform outputs here using:
        // output := terraform.Output(t, terraformOptions, "output_name")
}
```
```

Review S3 configuration:

```bash
python reviewer.py sample2.tf
```

Example output:

```text
Parsed: {'resources': [{'type': 'aws_s3_bucket', 'name': 'example'}]}
Security Findings: 1
Total Findings After AI: 4
Deduplicated: 4 -> 3
[HIGH] S3 Bucket Missing Encryption
[MEDIUM] S3 Bucket Without Versioning Enabled
[MEDIUM] S3 Bucket Missing Public Access Block Configuration

Total Risk Score: 20

Generated Terratest:
========================================

```go
package test

import (
        "testing"
        "path/filepath"

        "github.com/gruntwork-io/terratest/modules/terraform"
        "github.com/stretchr/testify/assert"
)

func TestTerraformModule(t *testing.T) {
        t.Parallel()

        terraformOptions := &terraform.Options{
                // The path to where your Terraform code is located
                TerraformDir: filepath.Join("..", "..", "terraform"),

                // Variables to pass to Terraform
                Vars: map[string]interface{}{},
        }

        // At the end of the test, run `terraform destroy` to clean up any resources that were created
        defer terraform.Destroy(t, terraformOptions)

        // Run `terraform init` and `terraform apply`. Fail the test if there are any errors.
        terraform.InitAndApply(t, terraformOptions)

        // Add assertions here to test the outputs or state
        output := terraform.Output(t, terraformOptions, "example_output")
        expected := "expected_value"
        assert.Equal(t, expected, output)
}
```

```

---

## Current Capabilities

* Terraform parsing
* Rule-based security checks
* AI-powered Terraform review
* Finding categorization
* Deduplication
* Risk scoring
* Terratest generation
* Shared workflow state model

---

## Roadmap

## Roadmap

- Conditional LangGraph routing
- Automated remediation generation
- Cost optimization analysis
- Terraform compliance checks
- Unit tests
- GitHub Actions CI/CD
- FastAPI REST API
- Multi-agent analysis workflows

---

## Learning Objectives

This project was built to explore:

- Python
- Terraform
- OpenAI APIs
- Prompt Engineering
- Infrastructure Security Analysis
- LangGraph
- Workflow Orchestration
- State Management
- AI-Assisted Developer Tools
- Rule Engines

---

## Version

All Release:
v0.1.0 - Initial Terraform AI Reviewer
v0.2.0 - LangGraph Workflow Engine
