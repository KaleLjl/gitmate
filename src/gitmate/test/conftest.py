"""Pytest configuration and fixtures for gitmate tests."""
import pytest
import yaml
from pathlib import Path
from typing import List, Dict, Any


@pytest.fixture
def test_dir():
    """Return the test directory path."""
    return Path(__file__).parent


@pytest.fixture
def user_intents(test_dir) -> List[str]:
    """Load all user intents from user_intents.yaml."""
    intents_file = test_dir / "user_intents.yaml"
    with open(intents_file, 'r', encoding='utf-8') as f:
        intents = yaml.safe_load(f)
    return intents if intents else []


@pytest.fixture
def git_contexts(test_dir) -> Dict[str, Dict[str, Any]]:
    """Load all git contexts from git_contexts/ directory."""
    contexts = {}
    contexts_dir = test_dir / "git_contexts"
    
    for context_file in sorted(contexts_dir.glob("*.yaml")):
        context_name = context_file.stem
        with open(context_file, 'r', encoding='utf-8') as f:
            context_data = yaml.safe_load(f)
            contexts[context_name] = context_data
    
    return contexts


@pytest.fixture
def mock_git_context(monkeypatch):
    """Factory fixture to mock get_git_context with custom context."""
    def _mock_context(context_dict: Dict[str, Any]):
        """Mock git_probes.get_git_context to return a specific context."""
        import yaml
        from gitmate import git_probes
        
        context_yaml = yaml.dump(
            context_dict,
            default_flow_style=False,
            allow_unicode=True,
            sort_keys=False
        ).strip()
        
        monkeypatch.setattr(
            git_probes,
            'get_git_context',
            lambda: context_yaml
        )
    
    return _mock_context


@pytest.fixture
def reports_dir(test_dir):
    """Create and return reports directory."""
    reports_path = test_dir / "reports"
    reports_path.mkdir(exist_ok=True)
    return reports_path

