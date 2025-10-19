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
        user_message: str,
        git_context_name: str,
        ai_response: str,
        expected_output: str = None,
        is_correct: bool = None
    ):
        """
        Add a test result with optional evaluation.
        
        Args:
            user_message: The user's natural language request
            git_context_name: Name of the git context scenario
            ai_response: The AI's response
            expected_output: The expected output (if available)
            is_correct: Whether the AI response matches expected (if evaluated)
        """
        result = {
            'user_message': user_message,
            'git_context_name': git_context_name,
            'ai_response': ai_response,
        }
        
        # Add evaluation data if available
        if expected_output is not None:
            result['expected_output'] = expected_output
            result['is_correct'] = is_correct
        
        self.results.append(result)
    
    def _organize_by_intent(self) -> List[Dict[str, Any]]:
        """Organize results by user message."""
        intent_map = {}
        
        for result in self.results:
            message = result['user_message']
            if message not in intent_map:
                intent_map[message] = {
                    'user_message': message,
                    'scenarios': []
                }
            
            scenario = {
                'git_context_name': result['git_context_name'],
                'ai_response': result['ai_response'],
            }
            
            # Add evaluation data if present
            if 'expected_output' in result:
                scenario['expected_output'] = result['expected_output']
                scenario['is_correct'] = result['is_correct']
            
            intent_map[message]['scenarios'].append(scenario)
        
        return list(intent_map.values())
    
    def _calculate_metrics(self) -> Dict[str, Any]:
        """Calculate comprehensive evaluation metrics."""
        total = len(self.results)
        evaluated = sum(1 for r in self.results if r.get('is_correct') is not None)
        
        if evaluated == 0:
            return {'note': 'No expected outputs provided for evaluation'}
        
        correct = sum(1 for r in self.results if r.get('is_correct') is True)
        incorrect = sum(1 for r in self.results if r.get('is_correct') is False)
        
        # Overall accuracy
        accuracy = (correct / evaluated) * 100 if evaluated > 0 else 0
        
        # Per-message accuracy
        message_stats = {}
        for result in self.results:
            if result.get('is_correct') is not None:
                message = result['user_message']
                if message not in message_stats:
                    message_stats[message] = {'correct': 0, 'total': 0}
                message_stats[message]['total'] += 1
                if result['is_correct']:
                    message_stats[message]['correct'] += 1
        
        message_accuracy = {
            message: round((data['correct'] / data['total']) * 100, 1)
            for message, data in message_stats.items()
        }
        
        # Per-context accuracy
        context_stats = {}
        for result in self.results:
            if result.get('is_correct') is not None:
                context = result['git_context_name']
                if context not in context_stats:
                    context_stats[context] = {'correct': 0, 'total': 0}
                context_stats[context]['total'] += 1
                if result['is_correct']:
                    context_stats[context]['correct'] += 1
        
        context_accuracy = {
            context: round((data['correct'] / data['total']) * 100, 1)
            for context, data in context_stats.items()
        }
        
        # Find problematic combinations (failures)
        failures = [
            {
                'user_message': r['user_message'],
                'git_context': r['git_context_name'],
            }
            for r in self.results
            if r.get('is_correct') is False
        ]
        
        return {
            'summary': {
                'total_tests': total,
                'evaluated_tests': evaluated,
                'correct': correct,
                'incorrect': incorrect,
                'accuracy_percent': round(accuracy, 2)
            },
            'per_message_accuracy': message_accuracy,
            'per_context_accuracy': context_accuracy,
            'failures_count': len(failures),
            'failed_combinations': failures[:20]  # Show top 20 failures
        }
    
    def generate_report(self, format: str = 'yaml') -> Path:
        """
        Generate and save the test report with metrics.
        
        Args:
            format: Output format ('yaml' or 'json')
        
        Returns:
            Path to the generated report file
        """
        end_time = datetime.now()
        duration = (end_time - self.start_time).total_seconds()
        
        # Organize results by user intent
        organized_results = self._organize_by_intent()
        
        # Calculate metrics
        metrics = self._calculate_metrics()
        
        # Build report structure
        report = {
            'test_run': {
                'timestamp': self.start_time.strftime("%Y-%m-%d %H:%M:%S"),
                'duration_seconds': round(duration, 2),
            },
            'metrics': metrics,
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

