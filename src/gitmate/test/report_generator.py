"""Report generator for test results."""
import json
import yaml
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any


class ReportGenerator:
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
        ai_response: str
    ):
        """
        Add a test result.
        
        Args:
            user_intent: The user's natural language request
            git_context_name: Name of the git context scenario
            ai_response: The AI's response
        """
        result = {
            'user_intent': user_intent,
            'git_context_name': git_context_name,
            'ai_response': ai_response,
        }
        
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
                'ai_response': result['ai_response'],
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
        
        # Organize results by user intent
        organized_results = self._organize_by_intent()
        
        # Build report structure
        report = {
            'test_run': {
                'timestamp': self.start_time.strftime("%Y-%m-%d %H:%M:%S"),
                'duration_seconds': round(duration, 2),
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

