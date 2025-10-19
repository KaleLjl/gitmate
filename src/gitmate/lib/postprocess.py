"""
GitMate Post-Processor - Context-aware command generation based on AI intent detection.
"""
import yaml
from typing import Dict, Optional
from gitmate.lib.intent_utils import validate_intent, get_intent_names


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
    
    def process(self, intent: str, git_context: Optional[Dict] = None) -> str:
        """
        Process AI intent and generate appropriate Git command.
        
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
        
        # Generate command based on intent
        if intent == "commit":
            return self._handle_commit(git_context)
        elif intent == "push":
            return self._handle_push(git_context)
        elif intent == "init":
            return self._handle_init(git_context)
        elif intent == "status":
            return self._handle_status(git_context)
        elif intent == "branch":
            return self._handle_branch(git_context)
        elif intent == "add":
            return self._handle_add(git_context)
        elif intent == "log":
            return self._handle_log(git_context)
        elif intent == "switch":
            return self._handle_switch(git_context)
        elif intent == "pull":
            return self._handle_pull(git_context)
        elif intent == "remote":
            return self._handle_remote(git_context)
        else:
            return f"Unhandled intent: {intent}"
    
    
    def _handle_commit(self, git_context: Optional[Dict]) -> str:
        """Handle commit intent with context awareness."""
        if not self.git_context_enabled or not git_context:
            return "git commit -m 'Update'"
        
        if not git_context.get("is_repo", False):
            return "Not a Git repository. Use 'git init' first."
        
        if not git_context.get("has_uncommitted", False):
            return "No changes to commit"
        
        # Check if there are unstaged files that need to be added
        if git_context.get("unstaged_count", 0) > 0:
            return "git add . && git commit -m 'Update'"
        else:
            return "git commit -m 'Update'"
    
    def _handle_push(self, git_context: Optional[Dict]) -> str:
        """Handle push intent with context awareness."""
        if not self.git_context_enabled or not git_context:
            return "git push"
        
        if not git_context.get("is_repo", False):
            return "Not a Git repository. Use 'git init' first."
        
        if not git_context.get("remote_exists", False):
            return "No remote repository configured. Use 'git remote add origin <url>' first"
        
        # Handle detached HEAD first
        if git_context.get("is_detached", False):
            if git_context.get("upstream_set", False):
                return "git push"
            else:
                return "git switch main && git push -u origin main"
        
        # Handle normal branch
        if git_context.get("upstream_set", False):
            return "git push"
        else:
            branch = git_context.get("branch", "main")
            return f"git push -u origin {branch}"
    
    def _handle_init(self, git_context: Optional[Dict]) -> str:
        """Handle init intent."""
        if not self.git_context_enabled or not git_context:
            return "git init"
        
        if git_context.get("is_repo", False):
            return "Repository already initialized"
        else:
            return "git init"
    
    def _handle_status(self, git_context: Optional[Dict]) -> str:
        """Handle status intent."""
        if not self.git_context_enabled or not git_context:
            return "git status"
        
        if not git_context.get("is_repo", False):
            return "Not a Git repository. Use 'git init' first."
        
        return "git status"
    
    def _handle_branch(self, git_context: Optional[Dict]) -> str:
        """Handle branch intent with context awareness."""
        if not self.git_context_enabled or not git_context:
            return "git branch"
        
        if not git_context.get("is_repo", False):
            return "Not a Git repository. Use 'git init' first."
        
        if git_context.get("is_detached", False):
            return "git checkout -b feature-branch"
        else:
            return "git branch feature-branch"
    
    def _handle_add(self, git_context: Optional[Dict]) -> str:
        """Handle add intent."""
        if not self.git_context_enabled or not git_context:
            return "git add ."
        
        if not git_context.get("is_repo", False):
            return "Not a Git repository. Use 'git init' first."
        
        return "git add ."
    
    def _handle_log(self, git_context: Optional[Dict]) -> str:
        """Handle log intent."""
        if not self.git_context_enabled or not git_context:
            return "git log --oneline"
        
        if not git_context.get("is_repo", False):
            return "Not a Git repository. Use 'git init' first."
        
        return "git log --oneline"
    
    def _handle_switch(self, git_context: Optional[Dict]) -> str:
        """Handle switch intent with context awareness."""
        if not self.git_context_enabled or not git_context:
            return "git switch main"
        
        if not git_context.get("is_repo", False):
            return "Not a Git repository. Use 'git init' first."
        
        if git_context.get("is_detached", False):
            return "git switch main"
        else:
            return "git switch main"
    
    def _handle_pull(self, git_context: Optional[Dict]) -> str:
        """Handle pull intent with context awareness."""
        if not self.git_context_enabled or not git_context:
            return "git pull"
        
        if not git_context.get("is_repo", False):
            return "Not a Git repository. Use 'git init' first."
        
        if not git_context.get("remote_exists", False):
            return "No remote repository configured. Use 'git remote add origin <url>' first"
        
        return "git pull"
    
    def _handle_remote(self, git_context: Optional[Dict]) -> str:
        """Handle remote intent."""
        if not self.git_context_enabled or not git_context:
            return "git remote -v"
        
        if not git_context.get("is_repo", False):
            return "Not a Git repository. Use 'git init' first."
        
        return "git remote -v"


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
