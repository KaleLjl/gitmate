# Gitmate Test Infrastructure

This test infrastructure validates AI responses against pre-defined user intents and git contexts.

## Overview

The test infrastructure runs a cross-product of all user intents against all git contexts, generating detailed reports of AI responses in each scenario.

## Directory Structure

```
test/
├── __init__.py
├── conftest.py              # Pytest fixtures and configuration
├── test_scenarios.py        # Main test runner
├── report_generator.py      # Report generation utility
├── user_intents.yaml        # List of user natural language requests
├── git_contexts/            # Directory of git context scenarios
│   ├── staged_files.yaml
│   ├── unstaged_changes.yaml
│   ├── clean_repo.yaml
│   ├── no_repo.yaml
│   ├── detached_head.yaml
│   ├── no_remote.yaml
│   └── no_upstream.yaml
├── reports/                 # Generated test reports (created automatically)
└── README.md               # This file
```

## User Intents

User intents are defined in `user_intents.yaml` as a simple list of natural language git requests:

```yaml
- "commit my changes"
- "push to remote"
- "initialize a repo"
```

Each intent will be tested against all git contexts.

## Git Contexts

Git contexts are defined as individual YAML files in the `git_contexts/` directory. Each file represents a different git repository state:

### Available Contexts

- **staged_files.yaml**: Repository with staged files ready to commit
- **unstaged_changes.yaml**: Repository with unstaged modifications
- **clean_repo.yaml**: Clean repository with no changes
- **no_repo.yaml**: Not a git repository
- **detached_head.yaml**: Repository in detached HEAD state
- **no_remote.yaml**: Repository without remote configured
- **no_upstream.yaml**: Branch without upstream tracking

### Context Format

```yaml
is_repo: true
branch: main
is_detached: false
staged_count: 2
unstaged_count: 0
has_uncommitted: true
remote_exists: true
upstream_set: true
```

## Running Tests

### Basic Usage

Run all test scenarios:

```bash
pytest src/gitmate/test/test_scenarios.py
```

### Verbose Output

To see detailed output during test execution:

```bash
pytest src/gitmate/test/test_scenarios.py -v -s
```

### Run from Project Root

```bash
cd /Users/lijialei/Work/gitmate
pytest src/gitmate/test/test_scenarios.py
```

## Test Reports

After running tests, reports are automatically generated in the `reports/` directory in both YAML and JSON formats:

- `test_report_YYYYMMDD_HHMMSS.yaml`
- `test_report_YYYYMMDD_HHMMSS.json`

### Report Structure

```yaml
test_run:
  timestamp: "2025-10-14 12:00:00"
  duration_seconds: 45.2
  total_tests: 70
  passed: 68
  failed: 2
  success_rate: "97.1%"

results:
  - user_intent: "commit my changes"
    scenarios:
      - git_context_name: "staged_files"
        git_context:
          is_repo: true
          branch: main
          staged_count: 2
          ...
        ai_response: |
          ```bash
          git commit -m "<msg>"
          ```
        status: "passed"
        
      - git_context_name: "unstaged_changes"
        git_context:
          is_repo: true
          unstaged_count: 3
          ...
        ai_response: |
          ```bash
          git add .
          git commit -m "<msg>"
          ```
        status: "passed"
```

## Adding New Test Cases

### Add a New User Intent

Edit `user_intents.yaml` and add a new line:

```yaml
- "your new user intent here"
```

### Add a New Git Context

Create a new YAML file in `git_contexts/`:

```bash
touch src/gitmate/test/git_contexts/your_context_name.yaml
```

Edit the file with the appropriate git state:

```yaml
is_repo: true
branch: feature-branch
is_detached: false
staged_count: 1
unstaged_count: 2
has_uncommitted: true
remote_exists: true
upstream_set: false
```

## Customization

### Change System Prompt

The tests use the `context_aware_prompt.md` by default. To change this, edit the `test_all_scenarios` method in `test_scenarios.py`:

```python
prompt_path = PROMPTS_DIR / "your_prompt.md"
```

### Modify Report Format

The `report_generator.py` can be customized to change report structure or add additional metrics.

## Interpreting Results

- **passed**: AI successfully generated a response (doesn't validate correctness, only that it ran)
- **failed**: An error occurred during AI response generation

The reports allow you to:
1. Review AI responses for each user intent across different git contexts
2. Identify patterns in how the AI handles different scenarios
3. Spot inconsistencies or unexpected behaviors
4. Validate that the AI follows the system prompt rules

## Dependencies

The test infrastructure requires:
- `pytest>=8.0.0`
- `pytest-mock>=3.12.0`
- All existing gitmate dependencies (mlx-lm, pyyaml, etc.)

These are automatically installed with the project dependencies.

