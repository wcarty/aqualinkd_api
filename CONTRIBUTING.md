# Contributing

Bug reports and pull requests are welcome.

## Before opening an issue

Include:

- Home Assistant version
- AqualinkD version and panel type
- Integration version
- Whether controls are enabled
- Relevant integration diagnostics with private network details redacted
- The exact entity or command that failed

Do not include passwords, access tokens, MQTT credentials, or private
certificates.

## Pull requests

1. Create a focused branch.
2. Follow [DEVELOPMENT.md](DEVELOPMENT.md).
3. Add or update tests for behavior changes.
4. Update user documentation for visible changes.
5. Confirm the **Validate** and **HACS** checks pass.

Changes that can operate physical equipment must remain opt-in and must refresh
the reported state from AqualinkD after the command.

## Security reports

Do not publish exploitable vulnerabilities or credentials in a public issue.
Use GitHub's private vulnerability reporting for this repository.
