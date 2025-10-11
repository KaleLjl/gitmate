from pathlib import Path


# System-level path configuration (not exposed to users)
SYSTEM_CONFIG = {
    'data_dir_name': '.gitmate',
    'conversations_dir': 'conversations',
    'prompts_dir': 'prompts',
    'repo_status_file': 'repo_status.yaml',
    'models_dir': 'models',
    'model_name': 'Qwen3-4B-Instruct-2507-MLX-4bit'
}

# Compute system paths
PACKAGE_ROOT = Path(__file__).resolve().parent
DATA_ROOT = Path.home() / SYSTEM_CONFIG['data_dir_name']
CONVERSATIONS_DIR = DATA_ROOT / SYSTEM_CONFIG['conversations_dir']
PROMPTS_DIR = PACKAGE_ROOT / SYSTEM_CONFIG['prompts_dir']
DEFAULT_REPO_STATUS_PATH = DATA_ROOT / SYSTEM_CONFIG['repo_status_file']
MODEL_PATH = PACKAGE_ROOT / SYSTEM_CONFIG['models_dir'] / SYSTEM_CONFIG['model_name']