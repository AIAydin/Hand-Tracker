# Contributing

Thanks for your interest in contributing! This document explains how to set up your environment, run the app, and submit changes.

## Getting started
1. Fork and clone the repository
2. Create a virtual environment and install dependencies:
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   pip install --upgrade pip
   pip install -r requirements.txt
   ```
3. Run the app:
   ```bash
   python -m hand_tracker.app --flip --width 640 --height 480
   ```

## Development workflow
- Branch naming: feature/my-change or fix/my-bug
- Commit style: concise, imperative (e.g., "Add finger counting overlay")
- Linting/formatting: keep code readable; PRs run basic CI checks
- Tests: add unit tests where possible (see tests/). Camera hardware is not required for tests.

## Pull requests
1. Create a PR with a clear description of the change and rationale
2. Link any related issues
3. Ensure CI passes (lint, tests)
4. Be responsive to review comments

## Reporting issues
- Include OS, Python version, and exact steps to reproduce
- Attach logs/tracebacks if possible

## Security
Please do not disclose vulnerabilities publicly. See SECURITY.md for the responsible disclosure process.

## Code of Conduct
By participating, you agree to abide by our CODE_OF_CONDUCT.md.

