"""
GitMate Post-Processor - Context-aware command generation based on AI intent detection.
"""
import yaml
from typing import Dict, Optional
from gitmate.lib.intent_utils import validate_intent, get_intent_names, get_expected_output


class RuleBasedPostProcessor:
    """
    Rule-based post-processor that generates Git commands based on AI intent and Git context.
    
    This class handles the conversion from intent (like 'commit', 'push') to actual Git commands
    with context-aware parameters based on the current Git repository state.
    """
    
    def __init__(self, git_context_enabled: bool):
        """
        Initialize the post-processor.
        
        Args:
            git_context_enabled: Whether to use Git context for command generation
        """
        self.git_context_enabled = git_context_enabled
        self.supported_intents = get_intent_names()
    
    def _map_git_context_to_name(self, git_context: Optional[Dict]) -> str:
        """Map runtime git context to predefined context name."""
        if not git_context or not git_context.get("is_repo", False):
            return "none"
        
        # Check for detached HEAD
        if git_context.get("is_detached", False):
            return "detached_remote_clean"
        
        # Check if remote exists
        remote_exists = git_context.get("remote_exists", False)
        upstream_set = git_context.get("upstream_set", False)
        
        # Determine staging state
        has_uncommitted = git_context.get("has_uncommitted", False)
        unstaged_count = git_context.get("unstaged_count", 0)
        staged_count = git_context.get("staged_count", 0)
        
        # Build context name
        if not remote_exists:
            prefix = "normal_noremote"
        elif not upstream_set:
            prefix = "normal_noupstream"
        else:
            prefix = "normal_remote"
        
        # Determine state suffix
        if not has_uncommitted:
            suffix = "clean"
        elif unstaged_count > 0 and staged_count > 0:
            suffix = "partial"
        elif unstaged_count > 0:
            suffix = "unstaged"
        elif staged_count > 0:
            suffix = "staged"
        else:
            suffix = "clean"
        
        return f"{prefix}_{suffix}"
    
    def process(self, intent: str, git_context: Optional[Dict] = None) -> str:
        """
        Process AI intent and generate appropriate Git command using data-driven lookup.
        
        Args:
            intent: The detected intent from AI (e.g., 'commit', 'push', 'status')
            git_context: Git repository context information
            
        Returns:
            str: Generated Git command or appropriate message
        """
        # Handle N/A cases
        if intent == "N/A":
            return "I can only help with Git operations. Please ask me about Git commands."
        
        # Handle unknown intents
        if not validate_intent(intent):
            return f"Unknown intent: {intent}"
        
        # Map git context to predefined context name
        context_name = self._map_git_context_to_name(git_context)
        
        # Look up expected output from intent_definitions.yaml
        expected_output = get_expected_output(intent, context_name)
        
        if expected_output and 'output' in expected_output:
            return expected_output['output']
        else:
            # Fallback for missing expected output
            return f"No handler for {intent} in context {context_name}"
    


def process_intent(intent: str, git_context_enabled: bool, git_context_str: str = None) -> str:
    """
    Convenience function to process intent with Git context.
    
    Args:
        intent: The detected intent from AI
        git_context_enabled: Whether Git context is enabled
        git_context_str: Git context as YAML string
        
    Returns:
        str: Generated Git command or message
    """
    # Parse Git context if provided
    git_context = None
    if git_context_enabled and git_context_str:
        try:
            git_context = yaml.safe_load(git_context_str) or {}
        except yaml.YAMLError:
            git_context = {}
    
    # Create post-processor and process intent
    post_processor = RuleBasedPostProcessor(git_context_enabled)
    return post_processor.process(intent, git_context)
