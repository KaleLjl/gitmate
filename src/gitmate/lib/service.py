"""
GitMate Service - Core pipeline logic for processing git-related messages.
"""
from gitmate.config import PROMPTS_DIR, MLX_MODEL, TRANSFORMERS_MODEL
from gitmate.lib.git_probes import get_git_context
from gitmate.lib.user_config import load_or_create_user_config
from gitmate.lib.history import save_conversation, update_conversation_with_ai_response
from gitmate.lib.postprocess import normalize_output, enforce_policies


class GitMateService:
    """
    Core service class that encapsulates the gitmate pipeline logic.
    
    This class handles configuration loading, prompt selection, AI response generation,
    and post-processing. It can be reused across different interfaces (CLI, interactive, etc.).
    """
    
    def __init__(self):
        """Initialize the service with configuration and prompt setup."""
        # Load user configuration once at initialization
        self.git_context_enabled, self.inference_engine = load_or_create_user_config()
        
        # Select prompt based on git context setting
        if self.git_context_enabled:
            self.selected_prompt = "context_aware_prompt.md"
        else:
            self.selected_prompt = "general_prompt.md"
        
        # Load system prompt
        self.system_prompt = self._load_system_prompt()
        
        # Model caching attributes
        self.model = None
        self.tokenizer = None
        self._model_loaded = False
    
    def _load_system_prompt(self) -> str:
        """Load the system prompt with validation."""
        prompt_path = PROMPTS_DIR / self.selected_prompt
        try:
            return prompt_path.read_text(encoding="utf-8")
        except FileNotFoundError:
            raise FileNotFoundError(
                f"Prompt file '{self.selected_prompt}' not found. "
                f"Available prompts: {list(PROMPTS_DIR.glob('*.md'))}"
            )
    
    def _get_git_context_str(self) -> str:
        """Get git context string if enabled, empty string otherwise."""
        if self.git_context_enabled:
            return get_git_context()
        return ""
    
    def _ensure_model_loaded(self):
        """Load model and tokenizer if not already loaded."""
        if not self._model_loaded:
            if self.inference_engine == 'mlx':
                from mlx_lm import load
                self.model, self.tokenizer = load(MLX_MODEL)
            elif self.inference_engine == 'transformers':
                import torch
                from transformers import AutoModelForCausalLM, AutoTokenizer
                
                # Auto-detect device (GPU if available, otherwise CPU)
                device = "cuda" if torch.cuda.is_available() else "cpu"
                
                # Load the model and tokenizer
                self.model = AutoModelForCausalLM.from_pretrained(
                    TRANSFORMERS_MODEL,
                    dtype=torch.float16 if device == "cuda" else torch.float32,
                    device_map="auto" if device == "cuda" else None
                )
                self.tokenizer = AutoTokenizer.from_pretrained(TRANSFORMERS_MODEL)
                
                # Move model to device if not using device_map
                if device == "cpu":
                    self.model = self.model.to(device)
                
                # Store device for later use
                self.device = device
            
            self._model_loaded = True
    
    def _get_ai_response_with_cached_model(self, message: str, git_context_str: str, system_prompt: str) -> str:
        """Get AI response using the cached model and tokenizer."""
        if self.inference_engine == 'mlx':
            return self._get_mlx_response(message, git_context_str, system_prompt)
        elif self.inference_engine == 'transformers':
            return self._get_transformers_response(message, git_context_str, system_prompt)
        else:
            raise ValueError(f"Unknown inference engine: {self.inference_engine}")
    
    def _get_mlx_response(self, message: str, git_context_str: str, system_prompt: str) -> str:
        """Get AI response using cached MLX model."""
        from mlx_lm import generate
        
        # Apply the prompt 
        prompt = (
            "User message: " + message
            + "\n\n---\n\nGit Context (YAML):\n```yaml\n"
            + git_context_str
            + "\n```\n\nEnd of context."
        )

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": prompt}
        ]
        
        formatted_prompt = self.tokenizer.apply_chat_template(
            messages, add_generation_prompt=True
        )

        result = generate(self.model, self.tokenizer, prompt=formatted_prompt, verbose=False)
        
        return result
    
    def _get_transformers_response(self, message: str, git_context_str: str, system_prompt: str) -> str:
        """Get AI response using cached Transformers model."""
        import torch
        
        # Apply the prompt 
        prompt = (
            "User message: " + message
            + "\n\n---\n\nGit Context (YAML):\n```yaml\n"
            + git_context_str
            + "\n```\n\nEnd of context."
        )

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": prompt}
        ]
        
        # Apply chat template
        formatted_prompt = self.tokenizer.apply_chat_template(
            messages, add_generation_prompt=True, tokenize=False
        )
        
        # Tokenize the prompt
        inputs = self.tokenizer(formatted_prompt, return_tensors="pt").to(self.device)
        
        # Generate response
        with torch.no_grad():
            outputs = self.model.generate(
                **inputs,
                max_new_tokens=512,
                do_sample=True,
                temperature=0.7,
                pad_token_id=self.tokenizer.eos_token_id
            )
        
        # Decode only the new tokens (response part)
        response_tokens = outputs[0][inputs['input_ids'].shape[1]:]
        result = self.tokenizer.decode(response_tokens, skip_special_tokens=True)
        
        return result
    
    def process_message(self, message: str) -> str:
        """
        Process a user message through the complete gitmate pipeline.
        
        Args:
            message: The user's natural language input
            
        Returns:
            The processed AI response as a string
        """
        # Ensure model is loaded (will only load once)
        self._ensure_model_loaded()
        
        # Get git context
        git_context_str = self._get_git_context_str()
        
        # Save user message to conversation history
        filepath = save_conversation(message)
        
        # Get AI response using cached model
        result = self._get_ai_response_with_cached_model(
            message, git_context_str, self.system_prompt
        )
        
        # Post-process the AI response
        try:
            result = normalize_output(result)
            result = enforce_policies(message, git_context_str, result)
        except Exception:
            # If post-processing fails, use the raw result
            pass
        
        # Update conversation file with AI response
        if not update_conversation_with_ai_response(filepath, result):
            raise RuntimeError("Failed to save AI response to conversation file")
        
        return result
