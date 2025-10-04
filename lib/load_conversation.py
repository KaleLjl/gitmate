"""
Load Conversation Module
Functions to load and process saved conversations
"""

import yaml
from pathlib import Path
from typing import Optional, Dict, Any
import os

def get_latest_conversation_file(conversations_dir: Path) -> Optional[Path]:
    """Get the most recently created conversation file"""
    yaml_files = list(conversations_dir.glob("*.yaml"))
    if not yaml_files:
        return None
    
    # Sort by modification time, most recent first
    latest_file = max(yaml_files, key=os.path.getmtime)
    return latest_file

def load_conversation_data(filepath: Path) -> Dict[str, Any]:
    """Load conversation data from YAML file"""
    try:
        with open(filepath, 'r', encoding='utf-8') as file:
            return yaml.safe_load(file)
    except yaml.YAMLError as e:
        raise ValueError(f"Error parsing YAML file {filepath}: {e}")
    except FileNotFoundError:
        raise FileNotFoundError(f"Conversation file not found: {filepath}")

def get_latest_user_message(conversations_dir: Path) -> Optional[str]:
    """Get the user_input from the latest conversation file"""
    latest_file = get_latest_conversation_file(conversations_dir)
    if not latest_file:
        return None
    
    conversation_data = load_conversation_data(latest_file)
    return conversation_data.get('user_input')

def update_conversation_with_response(filepath: Path, response: str) -> None:
    """Update conversation file with SLM response"""
    conversation_data = load_conversation_data(filepath)
    conversation_data['slm_response'] = response
    
    with open(filepath, 'w', encoding='utf-8') as file:
        yaml.dump(conversation_data, file, default_flow_style=False, allow_unicode=True)