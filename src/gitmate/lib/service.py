"""
GitMate Service - Core pipeline logic for processing git-related messages.
"""
from pathlib import Path
from gitmate.config import PROMPTS_DIR
from gitmate.lib.git_probes import get_git_context
from gitmate.lib.user_config import load_or_create_user_config
from gitmate.lib.history import save_conversation, update_conversation_with_ai_response
from gitmate.lib.anwser import get_ai_response
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
    
    def process_message(self, message: str) -> str:
        """
        Process a user message through the complete gitmate pipeline.
        
        Args:
            message: The user's natural language input
            
        Returns:
            The processed AI response as a string
        """
        # Get git context
        git_context_str = self._get_git_context_str()
        
        # Save user message to conversation history
        filepath = save_conversation(message)
        
        # Get AI response
        result = get_ai_response(
            self.inference_engine, 
            message, 
            git_context_str, 
            self.system_prompt
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
