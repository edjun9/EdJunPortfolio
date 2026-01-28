#!/usr/bin/env python3
"""
Advanced Harmony-format chatbot with config file support.
"""

import json
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict, Any


class AdvancedHarmonyChatbot:
    """Advanced chatbot using OpenAI Harmony format with configuration support."""
    
    # Special tokens in Harmony format
    SPECIAL_TOKENS = {
        "start": "<|start|>",
        "end": "<|end|>",
        "message": "<|message|>",
        "channel": "<|channel|>",
        "constrain": "<|constrain|>",
        "return": "<|return|>",
        "call": "<|call|>",
    }
    
    def __init__(self, config_file: str = "config.json", messages_file: str = "messages.json"):
        self.config_file = Path(config_file)
        self.messages_file = Path(messages_file)
        self.config = self._load_config()
        self.messages = self._load_messages()
    
    def _load_config(self) -> Dict[str, Any]:
        """Load configuration from JSON file."""
        if self.config_file.exists():
            with open(self.config_file, "r") as f:
                return json.load(f)
        return {
            "chatbot": {"name": "Harmony Chatbot"},
            "dummy_responses": {},
            "system_prompt": {"content": "You are a helpful assistant."}
        }
    
    def _load_messages(self) -> list:
        """Load conversation history from JSON file."""
        if self.messages_file.exists():
            with open(self.messages_file, "r") as f:
                return json.load(f)
        return []
    
    def _save_messages(self) -> None:
        """Save conversation history to JSON file."""
        with open(self.messages_file, "w") as f:
            json.dump(self.messages, f, indent=2)
    
    def _format_message(
        self,
        role: str,
        content: str,
        channel: str = "final",
        recipient: Optional[str] = None,
    ) -> str:
        """Format a message in Harmony format."""
        header = f"{role}"
        if recipient:
            header += f" to={recipient}"
        if channel:
            header = f"{self.SPECIAL_TOKENS['channel']}{channel} {header}"
        
        message = (
            f"{self.SPECIAL_TOKENS['start']}{header}"
            f"{self.SPECIAL_TOKENS['message']}{content}"
            f"{self.SPECIAL_TOKENS['end']}"
        )
        return message
    
    def _build_context(self) -> str:
        """Build the full Harmony format context for the conversation."""
        context = ""
        
        # Add system message
        system_prompt = self.config.get("system_prompt", {})
        system_content = system_prompt.get("content", "You are a helpful assistant.")
        context += self._format_message("system", system_content)
        
        # Add all previous messages
        for msg in self.messages:
            role = msg.get("role")
            content = msg.get("content")
            channel = msg.get("channel", "final")
            
            if role:
                context += self._format_message(role, content, channel=channel)
        
        return context
    
    def add_user_message(self, text: str) -> None:
        """Add a user message to conversation."""
        message = {
            "role": "user",
            "content": text,
            "channel": "final",
            "timestamp": datetime.now().isoformat(),
        }
        self.messages.append(message)
        self._save_messages()
    
    def add_assistant_message(
        self,
        text: str,
        channel: str = "final",
        is_cot: bool = False
    ) -> None:
        """Add an assistant message to conversation."""
        message = {
            "role": "assistant",
            "content": text,
            "channel": channel,
            "is_chain_of_thought": is_cot,
            "timestamp": datetime.now().isoformat(),
        }
        self.messages.append(message)
        self._save_messages()
    
    def get_dummy_response(self, user_input: str) -> str:
        """Generate a dummy response using config responses."""
        responses = self.config.get("dummy_responses", {})
        lower_input = user_input.lower()
        
        # Check for exact or partial matches
        for key, response in responses.items():
            if key != "default" and key in lower_input:
                return response
        
        # Return default response
        default = responses.get("default", f"You said: '{user_input}'. I'm a simple chatbot!")
        return default.format(input=user_input)
    
    def chat(self, user_input: str) -> str:
        """Process user input and generate response."""
        # Add user message
        self.add_user_message(user_input)
        
        # Generate dummy response
        response = self.get_dummy_response(user_input)
        
        # Add assistant response
        self.add_assistant_message(response, channel="final")
        
        return response
    
    def chat_with_reasoning(self, user_input: str) -> tuple[str, str]:
        """Chat with chain-of-thought (CoT) reasoning."""
        # Add user message
        self.add_user_message(user_input)
        
        # Generate reasoning
        reasoning = f"Thinking about: {user_input}"
        self.add_assistant_message(reasoning, channel="analysis", is_cot=True)
        
        # Generate response
        response = self.get_dummy_response(user_input)
        self.add_assistant_message(response, channel="final")
        
        return response, reasoning
    
    def display_conversation(self, include_cot: bool = False) -> None:
        """Display entire conversation history."""
        print("\n" + "="*70)
        print(f"CONVERSATION HISTORY - {self.config['chatbot'].get('name', 'Chatbot')}")
        print("="*70)
        
        for i, msg in enumerate(self.messages, 1):
            role = msg.get("role", "unknown").upper()
            channel = msg.get("channel", "N/A")
            is_cot = msg.get("is_chain_of_thought", False)
            
            # Skip CoT messages if not requested
            if is_cot and not include_cot:
                continue
            
            timestamp = msg.get("timestamp", "N/A")
            content = msg.get("content", "")
            
            print(f"\n[{i}] {role} (Channel: {channel}, CoT: {is_cot})")
            print(f"    Time: {timestamp}")
            print(f"    Content: {content[:100]}..." if len(content) > 100 else f"    Content: {content}")
        
        print("\n" + "="*70 + "\n")
    
    def get_harmony_export(self) -> str:
        """Export full conversation in Harmony format."""
        return self._build_context()
    
    def get_json_export(self) -> str:
        """Export conversation as formatted JSON."""
        return json.dumps(self.messages, indent=2)
    
    def get_stats(self) -> Dict[str, Any]:
        """Get conversation statistics."""
        user_msgs = sum(1 for m in self.messages if m.get("role") == "user")
        assistant_msgs = sum(1 for m in self.messages if m.get("role") == "assistant")
        cot_msgs = sum(1 for m in self.messages if m.get("is_chain_of_thought", False))
        
        total_chars = sum(len(m.get("content", "")) for m in self.messages)
        
        return {
            "total_messages": len(self.messages),
            "user_messages": user_msgs,
            "assistant_messages": assistant_msgs,
            "chain_of_thought_messages": cot_msgs,
            "total_characters": total_chars,
            "config_name": self.config.get("chatbot", {}).get("name"),
        }


def main():
    """Main chatbot loop with advanced features."""
    bot = AdvancedHarmonyChatbot()
    
    config_name = bot.config.get("chatbot", {}).get("name", "Chatbot")
    
    print("\n" + "="*70)
    print(f"{config_name} - ADVANCED VERSION")
    print("="*70)
    print("Commands:")
    print("  show       - Display conversation history")
    print("  show-cot   - Display including chain-of-thought")
    print("  harmony    - Show Harmony format output")
    print("  export     - Export as JSON")
    print("  stats      - Show conversation statistics")
    print("  quit       - Exit chatbot")
    print("="*70 + "\n")
    
    while True:
        try:
            user_input = input("You: ").strip()
            
            if not user_input:
                continue
            
            if user_input.lower() == "quit":
                print("Goodbye!")
                break
            
            if user_input.lower() == "show":
                bot.display_conversation(include_cot=False)
                continue
            
            if user_input.lower() == "show-cot":
                bot.display_conversation(include_cot=True)
                continue
            
            if user_input.lower() == "harmony":
                print("\nHarmony Format Output:")
                print("-" * 70)
                print(bot.get_harmony_export())
                print("-" * 70 + "\n")
                continue
            
            if user_input.lower() == "export":
                print("\nJSON Export:")
                print(bot.get_json_export())
                print()
                continue
            
            if user_input.lower() == "stats":
                stats = bot.get_stats()
                print("\nConversation Statistics:")
                for key, value in stats.items():
                    print(f"  {key}: {value}")
                print()
                continue
            
            # Regular chat
            response = bot.chat(user_input)
            print(f"Bot: {response}\n")
        
        except KeyboardInterrupt:
            print("\nGoodbye!")
            break
        except Exception as e:
            print(f"Error: {e}\n")


if __name__ == "__main__":
    main()
