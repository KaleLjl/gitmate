
from pathlib import Path

# System-level path configuration (not exposed to users)
SYSTEM_CONFIG = {
    'data_dir_name': '.gitmate',
    'conversations_dir': 'conversations',
    'prompts_dir': 'prompts',
    'repo_status_file': 'repo_status.yaml',
}

# Compute system paths
PACKAGE_ROOT = Path(__file__).resolve().parent
DATA_ROOT = Path.home() / SYSTEM_CONFIG['data_dir_name']
CONVERSATIONS_DIR = DATA_ROOT / SYSTEM_CONFIG['conversations_dir']
PROMPTS_DIR = PACKAGE_ROOT / SYSTEM_CONFIG['prompts_dir']
DEFAULT_REPO_STATUS_PATH = DATA_ROOT / SYSTEM_CONFIG['repo_status_file']
USER_CONFIG_PATH = DATA_ROOT / 'config.yaml'

# Model configuration
MODELS_DIR = DATA_ROOT / 'models'
MLX_MODEL_DIR = MODELS_DIR / 'mlx'
TRANSFORMERS_MODEL_DIR = MODELS_DIR / 'transformers'

# Hugging Face model IDs (used for downloading)
MLX_MODEL = 'mlx-community/Qwen2.5-3B-Instruct-4bit'
TRANSFORMERS_MODEL = 'Qwen/Qwen2.5-3B-Instruct'


