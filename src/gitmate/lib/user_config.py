import yaml
from gitmate.config import DATA_ROOT

# Create default configuration
default_config = {
    'git_context': True,
    'inference_engine': 'mlx'
}


def load_or_create_user_config():
    """
    Load user configuration from config.yaml.
    If the file doesn't exist, create it with default values.
    
    Returns:
        tuple: (git_context, inference_engine) - Direct values from config
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
        
        return default_config['git_context'], default_config['inference_engine']
    
    # Load existing configuration
    try:
        with open(config_path, 'r', encoding='utf-8') as file:
            config = yaml.safe_load(file)
            if config:
                git_context = config.get('git_context', True)
                inference_engine = config.get('inference_engine', 'mlx')
                return git_context, inference_engine
            else:
                return default_config['git_context'], default_config['inference_engine']
    except (yaml.YAMLError, FileNotFoundError):
        # If there's an error reading the file, return default config values
        return default_config['git_context'], default_config['inference_engine']
