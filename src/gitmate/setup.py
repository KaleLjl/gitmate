"""
GitMate Setup Script - Interactive setup for OS detection and model recommendation.
"""
import platform
import sys
from pathlib import Path
from typing import Dict, Any

try:
    import torch
    TORCH_AVAILABLE = True
except ImportError:
    TORCH_AVAILABLE = False

from gitmate.config import DATA_ROOT, MLX_MODEL_DIR, TRANSFORMERS_MODEL_DIR, MLX_MODEL, TRANSFORMERS_MODEL, USER_CONFIG_PATH


def detect_os_and_hardware() -> Dict[str, Any]:
    """
    Detect the current OS and hardware capabilities.
    
    Returns:
        Dict containing OS information, CPU architecture, and GPU availability
    """
    os_info = {
        'system': platform.system(),
        'machine': platform.machine(),
        'platform': platform.platform(),
        'gpu_available': False,
        'gpu_type': None
    }
    
    # Detect GPU availability
    if TORCH_AVAILABLE:
        if torch.cuda.is_available():
            os_info['gpu_available'] = True
            os_info['gpu_type'] = 'NVIDIA CUDA'
            os_info['gpu_count'] = torch.cuda.device_count()
        elif hasattr(torch.backends, 'mps') and torch.backends.mps.is_available():
            os_info['gpu_available'] = True
            os_info['gpu_type'] = 'Apple Metal Performance Shaders'
    else:
        os_info['gpu_available'] = False
        os_info['gpu_type'] = 'Unknown (PyTorch not available)'
    
    return os_info


def get_recommendation(os_info: Dict[str, Any]) -> str:
    """
    Get the recommended inference engine based on OS and hardware.
    
    Args:
        os_info: Dictionary containing OS and hardware information
        
    Returns:
        Recommended inference engine ('mlx' or 'transformers')
    """
    system = os_info['system']
    machine = os_info['machine']
    
    # macOS with Apple Silicon (arm64) - recommend MLX
    if system == 'Darwin' and machine == 'arm64':
        return 'mlx'
    
    # All other cases - recommend Transformers
    # This includes:
    # - macOS Intel
    # - Linux (any architecture)
    # - Windows (any architecture)
    return 'transformers'


def display_system_info(os_info: Dict[str, Any]) -> None:
    """Display detected system information."""
    print("🔍 System Detection Results:")
    print(f"   Operating System: {os_info['system']}")
    print(f"   Platform: {os_info['platform']}")
    print(f"   CPU Architecture: {os_info['machine']}")
    print(f"   GPU Available: {'Yes' if os_info['gpu_available'] else 'No'}")
    if os_info['gpu_available'] and os_info['gpu_type']:
        print(f"   GPU Type: {os_info['gpu_type']}")
        if 'gpu_count' in os_info:
            print(f"   GPU Count: {os_info['gpu_count']}")
    print()


def display_recommendation(recommendation: str, os_info: Dict[str, Any]) -> None:
    """Display the recommendation with explanation."""
    print("💡 Recommendation:")
    
    if recommendation == 'mlx':
        print("   Recommended: MLX")
        print("   Reason: You're on Apple Silicon (arm64), which is optimized for MLX")
        print("   Benefits: Faster inference, lower memory usage, native Apple Silicon support")
    else:
        print("   Recommended: Transformers")
        if os_info['system'] == 'Darwin' and os_info['machine'] != 'arm64':
            print("   Reason: You're on macOS Intel, which doesn't have optimized MLX support")
        elif os_info['system'] in ['Linux', 'Windows']:
            print("   Reason: MLX is not available on your operating system")
        print("   Benefits: Broad compatibility, CUDA support, extensive model support")
    
    print()


def prompt_user_choice(recommendation: str) -> str:
    """
    Prompt the user to choose their preferred inference engine.
    
    Args:
        recommendation: The recommended inference engine
        
    Returns:
        User's choice ('mlx' or 'transformers')
    """
    print("🎯 Choose your inference engine:")
    print(f"   [1] MLX (recommended for Apple Silicon)")
    print(f"   [2] Transformers (recommended for other platforms)")
    print()
    
    while True:
        try:
            choice = input(f"Enter your choice (1 or 2) [default: {'1' if recommendation == 'mlx' else '2'}]: ").strip()
            
            # Handle empty input (use recommendation as default)
            if not choice:
                return recommendation
            
            if choice == '1':
                return 'mlx'
            elif choice == '2':
                return 'transformers'
            else:
                print("❌ Invalid choice. Please enter 1 or 2.")
                
        except KeyboardInterrupt:
            print("\n\nSetup cancelled by user.")
            sys.exit(1)


def check_model_availability(model_path: Path) -> bool:
    """
    Check if model is already downloaded locally.
    
    Args:
        model_path: Path to the model directory
        
    Returns:
        True if model directory exists and contains model files
    """
    if not model_path.exists():
        return False
    
    # Check for common model files
    model_files = ['config.json', 'tokenizer.json', 'tokenizer_config.json']
    return any((model_path / file).exists() for file in model_files)


def download_model(model_id: str, target_dir: Path, model_type: str) -> Path:
    """
    Download model from Hugging Face Hub to local directory.
    
    Args:
        model_id: Hugging Face model ID
        target_dir: Local directory to download to
        model_type: Type of model (MLX or Transformers)
        
    Returns:
        Path to the downloaded model directory
    """
    from huggingface_hub import snapshot_download
    
    print(f"📥 Downloading {model_type} model: {model_id}")
    print(f"   Target directory: {target_dir}")
    print("   This may take a few minutes depending on your internet connection...")
    print()
    
    # Create target directory
    target_dir.mkdir(parents=True, exist_ok=True)
    
    try:
        model_path = snapshot_download(
            repo_id=model_id,
            local_dir=target_dir,
            resume_download=True,
            local_files_only=False
        )
        print(f"✅ {model_type} model downloaded successfully!")
        print(f"   Model path: {model_path}")
        return Path(model_path)
        
    except Exception as e:
        print(f"❌ Failed to download {model_type} model: {e}")
        print(f"   Please check your internet connection and try again.")
        raise


def download_selected_model(inference_engine: str) -> str:
    """
    Download the model for the selected inference engine.
    
    Args:
        inference_engine: Selected engine ('mlx' or 'transformers')
        
    Returns:
        Path to the downloaded model as string
    """
    if inference_engine == 'mlx':
        model_id = MLX_MODEL
        target_dir = MLX_MODEL_DIR
        model_type = "MLX"
    else:  # transformers
        model_id = TRANSFORMERS_MODEL
        target_dir = TRANSFORMERS_MODEL_DIR
        model_type = "Transformers"
    
    # Check if model already exists
    if check_model_availability(target_dir):
        print(f"✅ {model_type} model already downloaded at: {target_dir}")
        return str(target_dir)
    
    # Download the model
    model_path = download_model(model_id, target_dir, model_type)
    return str(model_path)


def update_config(inference_engine: str) -> None:
    """
    Update the configuration file with the selected inference engine.
    
    Args:
        inference_engine: The selected inference engine ('mlx' or 'transformers')
    """
    import yaml
    
    config_path = USER_CONFIG_PATH
    
    # Create DATA_ROOT directory if it doesn't exist
    DATA_ROOT.mkdir(parents=True, exist_ok=True)
    
    # Load existing config or create new one
    if config_path.exists():
        try:
            with open(config_path, 'r', encoding='utf-8') as file:
                config = yaml.safe_load(file) or {}
        except (yaml.YAMLError, FileNotFoundError):
            config = {}
    else:
        config = {}
    
    # Update the inference engine
    config['inference_engine'] = inference_engine
    
    # Ensure git_context is set (default to True if not present)
    if 'git_context' not in config:
        config['git_context'] = True
    
    # Write updated config
    try:
        with open(config_path, 'w', encoding='utf-8') as file:
            yaml.dump(config, file, default_flow_style=False, allow_unicode=True)
        
        print(f"✅ Configuration updated successfully!")
        print(f"   Inference Engine: {inference_engine}")
        print(f"   Config file: {config_path}")
        
    except Exception as e:
        print(f"❌ Failed to update configuration: {e}")
        sys.exit(1)


def confirm_setup(inference_engine: str) -> bool:
    """
    Confirm the setup choice with the user.
    
    Args:
        inference_engine: The selected inference engine
        
    Returns:
        True if user confirms, False otherwise
    """
    print(f"\n🔧 Setup Summary:")
    print(f"   Selected Engine: {inference_engine.upper()}")
    print(f"   Config Location: {USER_CONFIG_PATH}")
    print()
    
    while True:
        try:
            confirm = input("Proceed with this configuration? (y/n) [default: y]: ").strip().lower()
            
            if not confirm or confirm in ['y', 'yes']:
                return True
            elif confirm in ['n', 'no']:
                return False
            else:
                print("❌ Please enter 'y' for yes or 'n' for no.")
                
        except KeyboardInterrupt:
            print("\n\nSetup cancelled by user.")
            sys.exit(1)


def main():
    """Main setup function."""
    print("🚀 GitMate Setup")
    print("=" * 50)
    print()
    
    # Detect OS and hardware
    os_info = detect_os_and_hardware()
    display_system_info(os_info)
    
    # Get recommendation
    recommendation = get_recommendation(os_info)
    display_recommendation(recommendation, os_info)
    
    # Get user choice
    selected_engine = prompt_user_choice(recommendation)
    
    # Confirm setup
    if not confirm_setup(selected_engine):
        print("Setup cancelled. You can run 'gitmate-setup' again anytime.")
        return
    
    # Download the selected model
    try:
        download_selected_model(selected_engine)
    except Exception as e:
        print(f"\n❌ Setup failed during model download: {e}")
        print("You can run 'gitmate-setup' again to retry.")
        sys.exit(1)
    
    # Update configuration
    update_config(selected_engine)
    
    print()
    print("🎉 Setup complete!")
    print("You can now use GitMate with your selected configuration.")
    print("Run 'gitmate \"your git question\"' to get started!")


if __name__ == "__main__":
    main()
