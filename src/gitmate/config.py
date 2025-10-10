from pathlib import Path
import yaml

# Config file location
CONFIG_DIR = Path.home() / ".gitmate"
CONFIG_PATH = CONFIG_DIR / "config.yaml"

# Default configuration
DEFAULT_CONFIG = {
    "context_aware": True
}


def ensure_config():
    """
    Create config.yaml with default settings if it doesn't exist.
    
    Returns:
        Path: The path to the config file
    """
    if not CONFIG_PATH.exists():
        # Create the directory if it doesn't exist
        CONFIG_DIR.mkdir(parents=True, exist_ok=True)
        
        # Write default config
        with open(CONFIG_PATH, 'w', encoding='utf-8') as f:
            yaml.dump(DEFAULT_CONFIG, f, default_flow_style=False, allow_unicode=True)
    
    return CONFIG_PATH


def load_config():
    """
    Load and return the configuration from config.yaml.
    
    Returns:
        dict: Configuration dictionary with settings like {"context_aware": bool}
    """
    # Ensure config exists first
    ensure_config()
    
    # Load and return the config
    with open(CONFIG_PATH, 'r', encoding='utf-8') as f:
        config = yaml.safe_load(f)
    
    # Return default config if file is empty or invalid
    if config is None:
        return DEFAULT_CONFIG.copy()
    
    return config


def list_settings():
    """
    List all configuration settings and their current values.
    
    Returns:
        dict: Dictionary containing all configuration settings
    """
    config = load_config()
    return config


def update_config(key, value):
    """
    Update a configuration value and save it to config.yaml.
    
    Args:
        key (str): The configuration key to update (currently only "context_aware")
        value: The new value for the key
    
    Returns:
        bool: True if update was successful, False otherwise
    """
    # Validate key
    if key not in DEFAULT_CONFIG:
        print(f"Warning: '{key}' is not a valid configuration key.")
        return False
    
    # Validate value type for context_aware
    if key == "context_aware" and not isinstance(value, bool):
        print(f"Warning: '{key}' must be a boolean value.")
        return False
    
    # Load existing config
    config = load_config()
    
    # Update the value
    config[key] = value
    
    # Write back to file
    with open(CONFIG_PATH, 'w', encoding='utf-8') as f:
        yaml.dump(config, f, default_flow_style=False, allow_unicode=True)
    
    return True

