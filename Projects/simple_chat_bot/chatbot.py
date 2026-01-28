#!/usr/bin/env python3
"""
Simple Harmony-format chatbot with JSON message storage.
"""

import json
from datetime import datetime
from pathlib import Path
from typing import Optional


class HarmonyChatbot:
    """A simple chatbot using OpenAI Harmony response format."""
    
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
    
    def __init__(self, messages_file: str = "messages.json"):
        self.messages_file = Path(messages_file)
        self.messages = self._load_messages()
    
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
    
    def add_user_message(self, text: str) -> None:
        """Add a user message to conversation."""
        message = {
            "role": "user",
            "content": text,
            "timestamp": datetime.now().isoformat(),
            "harmony_format": self._format_message("user", text),
        }
        self.messages.append(message)
        self._save_messages()
    
    def add_assistant_message(self, text: str, channel: str = "final") -> None:
        """Add an assistant message to conversation."""
        message = {
            "role": "assistant",
            "content": text,
            "channel": channel,
            "timestamp": datetime.now().isoformat(),
            "harmony_format": self._format_message("assistant", text, channel=channel),
        }
        self.messages.append(message)
        self._save_messages()
    
    def get_dummy_response(self, user_input: str) -> str:
        """Generate a dummy response for testing."""
        responses = {
            "hello": "Hello! I'm a chatbot using Harmony format. How can I help you?",
            "how are you": "I'm working great! I'm using the OpenAI Harmony format.",
            "what is harmony": "Harmony is the response format for gpt-oss models. It uses special tokens like <|start|>, <|end|>, and <|message|>.",
            "default": f"You said: '{user_input}'. I'm a simple chatbot! Ask me something.",
        }
        
        lower_input = user_input.lower()
        for key, response in responses.items():
            if key in lower_input:
                return response
        
        return responses["default"]
    
    def chat(self, user_input: str) -> str:
        """Process user input and generate response."""
        # Add user message
        self.add_user_message(user_input)
        
        # Generate dummy response
        response = self.get_dummy_response(user_input)
        
        # Add assistant response
        self.add_assistant_message(response)
        
        return response
    
    def display_conversation(self) -> None:
        """Display entire conversation history."""
        print("\n" + "="*60)
        print("CONVERSATION HISTORY")
        print("="*60)
        for i, msg in enumerate(self.messages, 1):
            print(f"\n[{i}] {msg['role'].upper()} ({msg['timestamp']})")
            print(f"Content: {msg['content']}")
            if msg['role'] == 'assistant':
                print(f"Channel: {msg.get('channel', 'final')}")
            print(f"Harmony: {msg['harmony_format'][:100]}...")
        print("\n" + "="*60 + "\n")
    
    def get_json_export(self) -> str:
        """Export conversation as formatted JSON."""
        return json.dumps(self.messages, indent=2)


def main():
    """Main chatbot loop."""
    bot = HarmonyChatbot()
    
    print("\n" + "="*60)
    print("HARMONY FORMAT CHATBOT")
    print("="*60)
    print("Type 'quit' to exit, 'show' to display conversation")
    print("="*60 + "\n")
    
    while True:
        try:
            user_input = input("You: ").strip()
            
            if not user_input:
                continue
            
            if user_input.lower() == "quit":
                print("Goodbye!")
                break
            
            if user_input.lower() == "show":
                bot.display_conversation()
                continue
            
            if user_input.lower() == "export":
                print("\nJSON Export:")
                print(bot.get_json_export())
                continue
            
            # Chat with bot
            response = bot.chat(user_input)
            print(f"Bot: {response}\n")
        
        except KeyboardInterrupt:
            print("\nGoodbye!")
            break
        except Exception as e:
            print(f"Error: {e}")


if __name__ == "__main__":
    main()
