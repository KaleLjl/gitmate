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
        self._intent_mapping = self._load_intent_mapping()
    
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
    
    def _load_intent_mapping(self) -> Dict[str, str]:
        """Load intent definitions and create message-to-intent mapping."""
        try:
            # Get the path to intent_definitions.yaml relative to this file
            current_dir = Path(__file__).parent
            intent_file = current_dir.parent / "lib" / "intent_definitions.yaml"
            
            with open(intent_file, 'r', encoding='utf-8') as f:
                intent_data = yaml.safe_load(f)
            
            # Create mapping from example messages to intent names
            message_to_intent = {}
            for intent_name, intent_info in intent_data.get('intents', {}).items():
                for example in intent_info.get('examples', []):
                    message_to_intent[example] = intent_name
            
            return message_to_intent
        except Exception as e:
            print(f"Warning: Could not load intent definitions: {e}")
            return {}
    
    def _map_message_to_intent(self, user_message: str) -> str:
        """Map a user message to its corresponding intent."""
        return self._intent_mapping.get(user_message, 'unknown')
    
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
    
    def _organize_by_intent_then_context(self) -> List[Dict[str, Any]]:
        """Organize results by intent, then by git context, showing all messages for each combination."""
        intent_map = {}
        
        for result in self.results:
            message = result['user_message']
            intent = self._map_message_to_intent(message)
            git_context = result['git_context_name']
            
            # Initialize intent if not exists
            if intent not in intent_map:
                intent_map[intent] = {
                    'intent': intent,
                    'messages': set(),
                    'contexts': {}
                }
            
            # Add message to intent's message list
            intent_map[intent]['messages'].add(message)
            
            # Initialize context if not exists
            if git_context not in intent_map[intent]['contexts']:
                intent_map[intent]['contexts'][git_context] = {
                    'git_context_name': git_context,
                    'results_by_message': []
                }
            
            # Create result entry for this message-context combination
            message_result = {
                'message': message,
                'ai_response': result['ai_response']
            }
            
            # Add evaluation data if present
            if 'expected_output' in result:
                message_result['expected_output'] = result['expected_output']
                message_result['is_correct'] = result['is_correct']
            
            intent_map[intent]['contexts'][git_context]['results_by_message'].append(message_result)
        
        # Convert to list format and sort messages
        organized_results = []
        for intent_data in intent_map.values():
            intent_data['messages'] = sorted(list(intent_data['messages']))
            intent_data['contexts'] = list(intent_data['contexts'].values())
            organized_results.append(intent_data)
        
        # Sort by intent name
        organized_results.sort(key=lambda x: x['intent'])
        
        return organized_results
    
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
        
        # Per-intent accuracy
        intent_stats = {}
        for result in self.results:
            if result.get('is_correct') is not None:
                intent = self._map_message_to_intent(result['user_message'])
                if intent not in intent_stats:
                    intent_stats[intent] = {'correct': 0, 'total': 0}
                intent_stats[intent]['total'] += 1
                if result['is_correct']:
                    intent_stats[intent]['correct'] += 1
        
        intent_accuracy = {
            intent: round((data['correct'] / data['total']) * 100, 1)
            for intent, data in intent_stats.items()
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
            'per_intent_accuracy': intent_accuracy,
            'per_message_accuracy': message_accuracy,
            'per_context_accuracy': context_accuracy,
            'failures_count': len(failures),
            'failed_combinations': failures[:20]  # Show top 20 failures
        }
    
    def generate_report(self, format: str = 'yaml', organize_by_intent: bool = True) -> Path:
        """
        Generate and save the test report with metrics.
        
        Args:
            format: Output format ('yaml' or 'json')
            organize_by_intent: If True, organize by intent then context. If False, use original organization.
        
        Returns:
            Path to the generated report file
        """
        end_time = datetime.now()
        duration = (end_time - self.start_time).total_seconds()
        
        # Organize results by user intent
        if organize_by_intent:
            organized_results = self._organize_by_intent_then_context()
        else:
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

