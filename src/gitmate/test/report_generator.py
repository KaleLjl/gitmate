"""Report generator for test results."""
import json
import yaml
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any


class TestReportGenerator:
    """Generate test reports in YAML/JSON format."""
    
    def __init__(self, output_dir: Path):
        """
        Initialize the report generator.
        
        Args:
            output_dir: Directory where reports will be saved
        """
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.results = []
        self.start_time = datetime.now()
    
    def add_result(
        self,
        user_intent: str,
        git_context_name: str,
        git_context: Dict[str, Any],
        ai_response: str,
        error: str = None
    ):
        """
        Add a test result.
        
        Args:
            user_intent: The user's natural language request
            git_context_name: Name of the git context scenario
            git_context: The git context dictionary
            ai_response: The AI's response
            error: Error message if test failed, None if successful
        """
        result = {
            'user_intent': user_intent,
            'git_context_name': git_context_name,
            'git_context': git_context,
            'ai_response': ai_response,
            'status': 'failed' if error else 'passed',
        }
        
        if error:
            result['error'] = error
        
        self.results.append(result)
    
    def _organize_by_intent(self) -> List[Dict[str, Any]]:
        """Organize results by user intent."""
        intent_map = {}
        
        for result in self.results:
            intent = result['user_intent']
            if intent not in intent_map:
                intent_map[intent] = {
                    'user_intent': intent,
                    'scenarios': []
                }
            
            intent_map[intent]['scenarios'].append({
                'git_context_name': result['git_context_name'],
                'git_context': result['git_context'],
                'ai_response': result['ai_response'],
                'status': result['status'],
                'error': result.get('error')
            })
        
        return list(intent_map.values())
    
    def generate_report(self, format: str = 'yaml') -> Path:
        """
        Generate and save the test report.
        
        Args:
            format: Output format ('yaml' or 'json')
        
        Returns:
            Path to the generated report file
        """
        end_time = datetime.now()
        duration = (end_time - self.start_time).total_seconds()
        
        # Calculate statistics
        total_tests = len(self.results)
        passed_tests = sum(1 for r in self.results if r['status'] == 'passed')
        failed_tests = total_tests - passed_tests
        
        # Organize results by user intent
        organized_results = self._organize_by_intent()
        
        # Build report structure
        report = {
            'test_run': {
                'timestamp': self.start_time.strftime("%Y-%m-%d %H:%M:%S"),
                'duration_seconds': round(duration, 2),
                'total_tests': total_tests,
                'passed': passed_tests,
                'failed': failed_tests,
                'success_rate': f"{(passed_tests / total_tests * 100):.1f}%" if total_tests > 0 else "0%"
            },
            'results': organized_results
        }
        
        # Generate filename
        timestamp = self.start_time.strftime("%Y%m%d_%H%M%S")
        
        if format == 'json':
            filename = f"test_report_{timestamp}.json"
            filepath = self.output_dir / filename
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(report, f, indent=2, ensure_ascii=False)
        else:  # yaml
            filename = f"test_report_{timestamp}.yaml"
            filepath = self.output_dir / filename
            with open(filepath, 'w', encoding='utf-8') as f:
                yaml.dump(report, f, default_flow_style=False, allow_unicode=True, sort_keys=False)
        
        return filepath
    
    def print_summary(self):
        """Print a summary of test results to console."""
        total = len(self.results)
        passed = sum(1 for r in self.results if r['status'] == 'passed')
        failed = total - passed
        
        print("\n" + "=" * 60)
        print("TEST SUMMARY")
        print("=" * 60)
        print(f"Total Tests: {total}")
        print(f"Passed: {passed}")
        print(f"Failed: {failed}")
        print(f"Success Rate: {(passed / total * 100):.1f}%" if total > 0 else "0%")
        print("=" * 60 + "\n")

