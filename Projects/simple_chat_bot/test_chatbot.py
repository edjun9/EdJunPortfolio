#!/usr/bin/env python3
"""
Test suite for Harmony Format Chatbot.
Run with: python3 -m pytest test_chatbot.py -v
"""

import json
import tempfile
from pathlib import Path
from chatbot import HarmonyChatbot
from chatbot_advanced import AdvancedHarmonyChatbot


class TestHarmonyChatbot:
    """Test cases for basic HarmonyChatbot."""
    
    def setup_method(self):
        """Create temporary files for each test."""
        self.temp_dir = tempfile.mkdtemp()
        self.messages_file = Path(self.temp_dir) / "test_messages.json"
        self.bot = HarmonyChatbot(messages_file=str(self.messages_file))
    
    def test_initialization(self):
        """Test chatbot initialization."""
        assert self.bot is not None
        assert self.messages_file.exists()
    
    def test_add_user_message(self):
        """Test adding user message."""
        self.bot.add_user_message("Hello")
        assert len(self.bot.messages) == 1
        assert self.bot.messages[0]["role"] == "user"
        assert self.bot.messages[0]["content"] == "Hello"
    
    def test_add_assistant_message(self):
        """Test adding assistant message."""
        self.bot.add_assistant_message("Hi there!")
        assert len(self.bot.messages) == 1
        assert self.bot.messages[0]["role"] == "assistant"
        assert self.bot.messages[0]["content"] == "Hi there!"
    
    def test_message_persistence(self):
        """Test messages are saved to file."""
        self.bot.add_user_message("Test message")
        
        # Load new instance to check persistence
        bot2 = HarmonyChatbot(messages_file=str(self.messages_file))
        assert len(bot2.messages) == 1
        assert bot2.messages[0]["content"] == "Test message"
    
    def test_harmony_format(self):
        """Test Harmony format generation."""
        harmony = self.bot._format_message("user", "What is 2+2?")
        
        # Check for special tokens
        assert "<|start|>" in harmony
        assert "<|end|>" in harmony
        assert "<|message|>" in harmony
        assert "user" in harmony
        assert "What is 2+2?" in harmony
    
    def test_channel_in_harmony_format(self):
        """Test channel is included in Harmony format."""
        harmony = self.bot._format_message("assistant", "Response", channel="final")
        
        assert "<|channel|>final" in harmony
    
    def test_dummy_response(self):
        """Test dummy response generation."""
        response = self.bot.get_dummy_response("hello")
        assert response is not None
        assert len(response) > 0
    
    def test_chat_flow(self):
        """Test complete chat flow."""
        response = self.bot.chat("hello")
        
        assert len(self.bot.messages) == 2  # User + Assistant
        assert self.bot.messages[0]["role"] == "user"
        assert self.bot.messages[1]["role"] == "assistant"
        assert self.bot.messages[1]["content"] == response
    
    def test_json_export(self):
        """Test JSON export."""
        self.bot.chat("Hello")
        json_str = self.bot.get_json_export()
        
        # Should be valid JSON
        data = json.loads(json_str)
        assert isinstance(data, list)
        assert len(data) == 2
    
    def test_special_tokens(self):
        """Test all special tokens are defined."""
        expected_tokens = {
            "start": "<|start|>",
            "end": "<|end|>",
            "message": "<|message|>",
            "channel": "<|channel|>",
            "constrain": "<|constrain|>",
            "return": "<|return|>",
            "call": "<|call|>",
        }
        
        for token_name, token_value in expected_tokens.items():
            assert token_name in self.bot.SPECIAL_TOKENS
            assert self.bot.SPECIAL_TOKENS[token_name] == token_value


class TestAdvancedHarmonyChatbot:
    """Test cases for advanced AdvancedHarmonyChatbot."""
    
    def setup_method(self):
        """Create temporary files for each test."""
        self.temp_dir = tempfile.mkdtemp()
        self.config_file = Path(self.temp_dir) / "test_config.json"
        self.messages_file = Path(self.temp_dir) / "test_messages.json"
        
        # Create a test config
        test_config = {
            "chatbot": {"name": "Test Bot"},
            "dummy_responses": {
                "hello": "Hello, test!",
                "default": "Test response"
            },
            "system_prompt": {"content": "Test system prompt"}
        }
        with open(self.config_file, "w") as f:
            json.dump(test_config, f)
        
        self.bot = AdvancedHarmonyChatbot(
            config_file=str(self.config_file),
            messages_file=str(self.messages_file)
        )
    
    def test_config_loading(self):
        """Test configuration is loaded correctly."""
        assert self.bot.config["chatbot"]["name"] == "Test Bot"
    
    def test_chat_with_reasoning(self):
        """Test chat with reasoning."""
        response, reasoning = self.bot.chat_with_reasoning("hello")
        
        assert len(self.bot.messages) == 3  # User + CoT + Assistant
        assert self.bot.messages[1]["is_chain_of_thought"] == True
        assert "hello" in reasoning.lower()
    
    def test_build_context(self):
        """Test context building."""
        self.bot.chat("test")
        context = self.bot._build_context()
        
        assert "<|start|>" in context
        assert "<|end|>" in context
        assert "system" in context
        assert "user" in context
        assert "assistant" in context
    
    def test_harmony_export(self):
        """Test Harmony format export."""
        self.bot.chat("hello")
        harmony = self.bot.get_harmony_export()
        
        assert "<|start|>" in harmony
        assert "<|end|>" in harmony
        assert len(harmony) > 100
    
    def test_statistics(self):
        """Test statistics generation."""
        self.bot.chat("hello")
        self.bot.chat("how are you")
        
        stats = self.bot.get_stats()
        
        assert stats["total_messages"] == 4  # 2 user + 2 assistant
        assert stats["user_messages"] == 2
        assert stats["assistant_messages"] == 2
        assert stats["config_name"] == "Test Bot"
    
    def test_multiple_channels(self):
        """Test messages with different channels."""
        self.bot.add_user_message("test")
        self.bot.add_assistant_message("response1", channel="analysis", is_cot=True)
        self.bot.add_assistant_message("response2", channel="final")
        
        assert self.bot.messages[1]["channel"] == "analysis"
        assert self.bot.messages[2]["channel"] == "final"


class TestHarmonyFormatCompliance:
    """Test Harmony format compliance."""
    
    def setup_method(self):
        """Create chatbot instance."""
        self.temp_dir = tempfile.mkdtemp()
        self.messages_file = Path(self.temp_dir) / "test_messages.json"
        self.bot = HarmonyChatbot(messages_file=str(self.messages_file))
    
    def test_message_structure(self):
        """Test message follows Harmony structure."""
        harmony = self.bot._format_message("user", "test")
        
        # Structure: <|start|>{header}<|message|>{content}<|end|>
        parts = harmony.split("<|message|>")
        assert len(parts) == 2
        
        header_part = parts[0]
        content_part = parts[1]
        
        assert header_part.startswith("<|start|>")
        assert content_part.endswith("<|end|>")
    
    def test_channel_placement(self):
        """Test channel is placed correctly in header."""
        harmony = self.bot._format_message("assistant", "test", channel="analysis")
        
        # Channel should appear after <|start|> and before <|message|>
        start_idx = harmony.find("<|start|>")
        channel_idx = harmony.find("<|channel|>")
        message_idx = harmony.find("<|message|>")
        
        assert start_idx < channel_idx < message_idx
    
    def test_role_in_message(self):
        """Test role is included in message."""
        for role in ["user", "assistant", "system"]:
            harmony = self.bot._format_message(role, "test")
            assert role in harmony
    
    def test_metadata_preservation(self):
        """Test message metadata is preserved."""
        self.bot.add_user_message("test message")
        msg = self.bot.messages[0]
        
        assert "timestamp" in msg
        assert "role" in msg
        assert "content" in msg
        assert "harmony_format" in msg


class TestEdgeCases:
    """Test edge cases and error handling."""
    
    def setup_method(self):
        """Create chatbot instance."""
        self.temp_dir = tempfile.mkdtemp()
        self.messages_file = Path(self.temp_dir) / "test_messages.json"
        self.bot = HarmonyChatbot(messages_file=str(self.messages_file))
    
    def test_empty_message(self):
        """Test handling of empty messages."""
        self.bot.add_user_message("")
        assert len(self.bot.messages) == 1
        assert self.bot.messages[0]["content"] == ""
    
    def test_long_message(self):
        """Test handling of very long messages."""
        long_message = "x" * 10000
        self.bot.add_user_message(long_message)
        assert self.bot.messages[0]["content"] == long_message
    
    def test_special_characters(self):
        """Test messages with special characters."""
        special_msg = 'Test with "quotes" and \'apostrophes\' & <symbols>'
        self.bot.add_user_message(special_msg)
        assert self.bot.messages[0]["content"] == special_msg
    
    def test_unicode_characters(self):
        """Test messages with unicode characters."""
        unicode_msg = "你好世界 🌍 مرحبا العالم"
        self.bot.add_user_message(unicode_msg)
        assert self.bot.messages[0]["content"] == unicode_msg
    
    def test_json_export_validity(self):
        """Test JSON export is always valid."""
        test_messages = [
            "normal message",
            "",
            "x" * 1000,
            'Test with "quotes"',
            "Unicode: 你好",
        ]
        
        for msg in test_messages:
            self.bot.add_user_message(msg)
        
        # Should not raise exception
        json_str = self.bot.get_json_export()
        data = json.loads(json_str)
        assert len(data) > 0


def test_import_modules():
    """Test that all modules can be imported."""
    from chatbot import HarmonyChatbot
    from chatbot_advanced import AdvancedHarmonyChatbot
    assert HarmonyChatbot is not None
    assert AdvancedHarmonyChatbot is not None


if __name__ == "__main__":
    # Run tests with pytest
    import sys
    import pytest
    
    # Run tests
    exit_code = pytest.main([__file__, "-v", "--tb=short"])
    sys.exit(exit_code)
