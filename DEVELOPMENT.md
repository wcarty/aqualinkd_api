# Development Guidelines

This document outlines the development workflow, security practices, and automation used in the AqualinkD API project.

## 🚀 AI-Powered Workflow

We use AI to ensure high code quality, security, and maintainability. Our CI/CD pipeline includes:

### 1. AI Code Review
Every Pull Request is automatically reviewed by an AI agent (using GPT-4o).
- **What it does**: Analyzes the diff, identifies logic flaws, suggests performance improvements, and ensures adherence to coding standards.
- **How to use**: Simply open a PR. The AI will comment with its findings. You can interact with the AI by replying to its comments if the specific action supports it.

### 2. Automated Security Scanning
We use **GitHub CodeQL** and AI-driven security analysis to catch vulnerabilities early.
- **CodeQL**: Performs static analysis to find common security patterns (SQL injection, XSS, etc.).
- **AI Security Review**: The PR reviewer is specifically prompted to look for security risks in the context of Home Assistant integrations (e.g., credential handling, local network security).

### 3. Dependency Management
**Dependabot** is enabled to keep our dependencies updated and secure.
- It scans for outdated or vulnerable packages weekly.
- Automatically opens PRs to update requirements.

## 🛠️ Local Development

### Setup
1. Clone the repository.
2. Install development dependencies:
   ```bash
   pip install ruff pytest
   ```

### Linting & Formatting
We use **Ruff** for extremely fast linting and formatting.
- Run linting: `ruff check .`
- Auto-fix issues: `ruff check --fix .`

### Testing
You can run tests locally using a virtual environment and `dev-requirements.txt`.

```powershell
python -m venv .venv
.venv\Scripts\python.exe -m pip install --upgrade pip
.venv\Scripts\python.exe -m pip install -r dev-requirements.txt
.venv\Scripts\python.exe -m ruff check . --fix
.venv\Scripts\python.exe -m pytest -q
```

Tests are lightweight and avoid depending on Home Assistant; they exercise core logic in `custom_components/aqualinkd_api`.

## 🔒 Security Best Practices

1. **No Hardcoded Secrets**: Never hardcode IP addresses, passwords, or tokens in the codebase. Use configuration flows.
2. **Input Validation**: Always validate data received from the AqualinkD API before processing.
3. **Local Only**: Ensure the integration remains strictly local-polling and does not leak data to external services unless explicitly configured.
4. **SSL Verification**: While disabled by default for ease of use with local self-signed certs, we encourage users to enable `verify_ssl` when using HTTPS.

## 🤝 Contribution Workflow

1. **Fork & Branch**: Create a feature branch for your changes.
2. **Lint**: Run `ruff check .` before committing.
3. **Test**: Ensure `test_merge.py` passes.
4. **PR**: Open a PR. Wait for the AI Reviewer and CI checks to pass.
5. **Address Feedback**: Review both human and AI comments.
