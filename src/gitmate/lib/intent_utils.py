"""
Simple utility functions for working with intents.
Provides centralized access to intent definitions across GitMate components.
"""
import yaml
from pathlib import Path
from typing import Dict, List, Optional

def load_intents(intents_file: Optional[Path] = None) -> Dict:
    """Load intents from YAML file."""
    if intents_file is None:
        intents_file = Path(__file__).parent / "intent_definitions.yaml"
    
    with open(intents_file, 'r', encoding='utf-8') as f:
        return yaml.safe_load(f)

def get_intent_names() -> List[str]:
    """Get list of all intent names."""
    intents = load_intents()
    return list(intents['intents'].keys())

def get_git_intent_names() -> List[str]:
    """Get list of Git command intent names (excluding N/A)."""
    intents = load_intents()
    return [name for name in intents['intents'].keys() if name != 'N/A']

def get_intent_examples(intent_name: str) -> List[str]:
    """Get examples for a specific intent."""
    intents = load_intents()
    return intents['intents'].get(intent_name, {}).get('examples', [])

def get_all_examples() -> List[str]:
    """Get all examples for testing."""
    intents = load_intents()
    examples = []
    for intent_data in intents['intents'].values():
        examples.extend(intent_data.get('examples', []))
    return examples

def get_intent_mapping() -> Dict[str, str]:
    """Get mapping from example messages to intent names."""
    intents = load_intents()
    message_to_intent = {}
    for intent_name, intent_data in intents['intents'].items():
        for example in intent_data.get('examples', []):
            message_to_intent[example] = intent_name
    return message_to_intent

def validate_intent(intent_name: str) -> bool:
    """Check if intent name is valid."""
    return intent_name in get_intent_names()

def generate_prompt_content() -> str:
    """Generate the intent detection prompt from YAML."""
    intents = load_intents()
    
    lines = [
        "# GitMate Intent Detection",
        "",
        "You are a Git intent detection system. Analyze the user's message and determine which Git command they want to execute.",
        "",
        "## Available Intents",
        "",
        "Output ONLY one of these intent commands:",
        ""
    ]
    
    for name, intent_data in intents['intents'].items():
        description = intent_data['description']
        examples = intent_data.get('examples', [])
        
        lines.append(f"- **{name}** - {description}")
        if examples:
            examples_str = ", ".join([f'"{ex}"' for ex in examples[:3]])
            lines.append(f"  Examples: {examples_str}")
    
    lines.extend([
        "",
        "## Instructions",
        "",
        "1. Analyze the user's natural language input",
        "2. Determine which Git command they want to execute", 
        "3. If the input is not related to Git operations, output N/A",
        "4. Output ONLY the intent command name",
        "5. Do not output any explanation or additional text",
        "",
        "**IMPORTANT: Output only the command name, nothing else.**"
    ])
    
    return "\n".join(lines)
