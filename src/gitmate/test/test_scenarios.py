"""Test scenarios for gitmate AI responses."""
import pytest
from pathlib import Path
from gitmate.anwser import get_ai_response
from gitmate.system_config import PROMPTS_DIR
from gitmate.test.report_generator import ReportGenerator


class TestScenarios:
    """Test AI responses across different user intents and git contexts."""
    
    @pytest.fixture(autouse=True)
    def setup(self, reports_dir):
        """Setup test report generator."""
        self.report_generator = ReportGenerator(reports_dir)
    
    def test_all_scenarios(self, user_intents, git_contexts, mock_git_context):
        """
        Test all combinations of user intents and git contexts.
        
        This test creates a cross-product of all user intents and git contexts,
        running each user intent against every git context scenario.
        """
        # Load the system prompt (using context-aware prompt)
        prompt_path = PROMPTS_DIR / "context_aware_prompt.md"
        
        try:
            system_prompt = prompt_path.read_text(encoding="utf-8")
        except FileNotFoundError:
            pytest.fail(f"System prompt not found at {prompt_path}")
        
        # Iterate through each user intent
        for user_intent in user_intents:
            print(f"Testing: {user_intent}")
            # Test against each git context
            for context_name, context_data in git_contexts.items():
                print(f"  - {context_name}")
                # Mock the git context
                mock_git_context(context_data)
                
                try:
                    # Get AI response
                    ai_response = get_ai_response(
                        message=user_intent,
                        git_context_str=self._format_context(context_data),
                        system_prompt=system_prompt
                    )
                    
                    # Record result
                    self.report_generator.add_result(
                        user_intent=user_intent,
                        git_context_name=context_name,
                        ai_response=ai_response
                    )
                    
                except Exception as e:
                    # Record failed result
                    self.report_generator.add_result(
                        user_intent=user_intent,
                        git_context_name=context_name,
                        ai_response=""
                    )
    
    def _format_context(self, context_dict):
        """Format git context dict as YAML string."""
        import yaml
        return yaml.dump(
            context_dict,
            default_flow_style=False,
            allow_unicode=True,
            sort_keys=False
        ).strip()
    
    @pytest.fixture(autouse=True)
    def generate_report(self, request):
        """Generate report after all tests complete."""
        yield
        
        # This runs after the test
        if hasattr(self, 'report_generator'):
            # Generate both YAML and JSON reports
            yaml_report = self.report_generator.generate_report(format='yaml')
            json_report = self.report_generator.generate_report(format='json')
