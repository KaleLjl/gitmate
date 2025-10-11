import yaml
from pathlib import Path
from gitmate.system_config import (
    DATA_ROOT
)

 # Create default configuration
default_config = {
            'git_context': True
        }
def load_or_create_user_config():
    """
    Load user configuration from config.yaml.
    If the file doesn't exist, create it with default values.
    
    Returns:
        dict: User configuration dictionary
    """
    # Define the config file path
    config_path = DATA_ROOT / "config.yaml"
    
    # Create DATA_ROOT directory if it doesn't exist
    DATA_ROOT.mkdir(parents=True, exist_ok=True)
    
    # Check if config file exists
    if not config_path.exists():
        # Write default config to file
        with open(config_path, 'w', encoding='utf-8') as file:
            yaml.dump(default_config, file, default_flow_style=False, allow_unicode=True)
        
        return default_config
    
    # Load existing configuration
    try:
        with open(config_path, 'r', encoding='utf-8') as file:
            config = yaml.safe_load(file)
            return config if config else {}
    except (yaml.YAMLError, FileNotFoundError):
        # If there's an error reading the file, return default config
        return {'git_context': True}
