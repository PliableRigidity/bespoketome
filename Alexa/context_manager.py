# context_manager.py
from collections import deque
from typing import List, Dict

class ConversationContext:
    """Manages conversation history for context-aware responses."""
    
    def __init__(self, max_history: int = 10):
        """
        Initialize conversation context.
        
        Args:
            max_history: Maximum number of conversation turns to remember
        """
        self.max_history = max_history
        self.history = deque(maxlen=max_history)
    
    def add_turn(self, user_message: str, assistant_response: str):
        """
        Add a conversation turn to history.
        
        Args:
            user_message: What the user said
            assistant_response: What the assistant responded
        """
        self.history.append({
            "user": user_message,
            "assistant": assistant_response
        })
    
    def get_context_messages(self) -> List[Dict[str, str]]:
        """
        Get conversation history formatted for LLM.
        
        Returns:
            List of message dicts with 'role' and 'content'
        """
        messages = []
        for turn in self.history:
            messages.append({"role": "user", "content": turn["user"]})
            messages.append({"role": "assistant", "content": turn["assistant"]})
        return messages
    
    def clear(self):
        """Clear all conversation history."""
        self.history.clear()
    
    def get_summary(self) -> str:
        """Get a text summary of recent conversation."""
        if not self.history:
            return "No previous conversation."
        
        summary_parts = []
        for i, turn in enumerate(self.history, 1):
            summary_parts.append(f"Turn {i}:")
            summary_parts.append(f"  User: {turn['user']}")
            summary_parts.append(f"  Assistant: {turn['assistant']}")
        
        return "\n".join(summary_parts)

# Global context instance
_global_context = ConversationContext(max_history=10)

def get_context() -> ConversationContext:
    """Get the global conversation context."""
    return _global_context
