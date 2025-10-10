from pathlib import Path
import yaml

# System-level path configuration (not exposed to users)
SYSTEM_CONFIG = {
    'data_dir_name': '.gitmate',
    'conversations_dir': 'conversations',
    'prompts_dir': 'prompts',
    'context_prompt_file': 'context_aware_prompt.md',
    'repo_status_file': 'repo_status.yaml',
    'models_dir': 'models',
    'model_name': 'Qwen3-4B-Instruct-2507-MLX-4bit'
}

# Compute system paths
PACKAGE_ROOT = Path(__file__).resolve().parent
DATA_ROOT = Path.home() / SYSTEM_CONFIG['data_dir_name']
CONVERSATIONS_DIR = DATA_ROOT / SYSTEM_CONFIG['conversations_dir']
PROMPT_PATH = PACKAGE_ROOT / SYSTEM_CONFIG['prompts_dir'] / SYSTEM_CONFIG['context_prompt_file']
DEFAULT_REPO_STATUS_PATH = DATA_ROOT / SYSTEM_CONFIG['repo_status_file']
MODEL_PATH = PACKAGE_ROOT / SYSTEM_CONFIG['models_dir'] / SYSTEM_CONFIG['model_name']

# User config file location
CONFIG_DIR = Path.home() / ".gitmate"
CONFIG_PATH = CONFIG_DIR / "config.yaml"

# Default user configuration
DEFAULT_CONFIG = {
    "context_aware": True
}
