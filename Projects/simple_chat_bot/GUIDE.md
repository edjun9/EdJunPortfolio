# Harmony Format Chatbot - Complete Guide

This project implements a chatbot using OpenAI's **Harmony response format**, complete with JSON message storage, multiple channels, and chain-of-thought reasoning.

## Table of Contents

1. [Quick Start](#quick-start)
2. [Project Structure](#project-structure)
3. [Features](#features)
4. [Harmony Format Overview](#harmony-format-overview)
5. [Usage Examples](#usage-examples)
6. [API Reference](#api-reference)
7. [Configuration](#configuration)
8. [Advanced Features](#advanced-features)

## Quick Start

### Run the Basic Chatbot

```bash
python3 chatbot.py
```

### Run the Advanced Chatbot

```bash
python3 chatbot_advanced.py
```

### Run All Demos

```bash
python3 demo.py
```

## Project Structure

```
simple_chat_bot/
├── chatbot.py                 # Basic chatbot implementation
├── chatbot_advanced.py        # Advanced chatbot with config support
├── demo.py                    # Comprehensive demo script
├── config.json                # Chatbot configuration
├── messages.json              # Conversation history (auto-generated)
├── README.md                  # Project overview
├── GUIDE.md                   # This file
└── AGENTS.md                  # Agent instructions (if present)
```

## Features

### 1. Harmony Format Compliance
- All messages formatted according to OpenAI Harmony specification
- Special tokens: `<|start|>`, `<|end|>`, `<|message|>`, `<|channel|>`, `<|return|>`, `<|call|>`
- Proper message headers with role, channel, and metadata

### 2. Message Storage
- **JSON Storage**: All messages saved in `messages.json` with metadata
- **Persistent History**: Conversation continues across sessions
- **Timestamped**: Each message includes ISO 8601 timestamp
- **Structured Format**: Easy to parse and analyze

### 3. Multi-Channel Support
- **final**: User-facing responses
- **analysis**: Internal chain-of-thought (not shown to users)
- **commentary**: Preambles, action plans, tool calls

### 4. Conversation Management
- Add user and assistant messages
- Track message metadata (role, channel, timestamp)
- Export in multiple formats (JSON, Harmony format)
- View conversation history with formatting

### 5. Configuration
- External `config.json` for customization
- Define system prompts, dummy responses, metadata
- Easy to extend with new features

## Harmony Format Overview

### What is Harmony?

Harmony is the response format for gpt-oss models, designed to mimic the OpenAI Responses API with special tokens for message structure and metadata.

### Message Structure

```
<|start|>{header}<|message|>{content}<|end|>
```

### Example Messages

**System Message:**
```
<|start|><|channel|>final system<|message|>You are a helpful assistant.<|end|>
```

**User Message:**
```
<|start|><|channel|>final user<|message|>What is 2 + 2?<|end|>
```

**Assistant Response:**
```
<|start|><|channel|>final assistant<|message|>2 + 2 = 4.<|end|>
```

### Special Tokens

| Token | Purpose | ID |
|-------|---------|-----|
| `<|start|>` | Message begin | 200006 |
| `<|end|>` | Message end | 200007 |
| `<|message|>` | Header/content transition | 200008 |
| `<|channel|>` | Channel specification | 200005 |
| `<|constrain|>` | Data type definition | 200003 |
| `<|return|>` | Completion end | 200002 |
| `<|call|>` | Tool call | 200012 |

### Channels

| Channel | Purpose | Examples |
|---------|---------|----------|
| **final** | User-facing output | Main responses shown to user |
| **analysis** | Chain-of-thought | Internal reasoning, not shown |
| **commentary** | Preambles & tool calls | Action plans, tool calls |

## Usage Examples

### Example 1: Basic Conversation

```python
from chatbot import HarmonyChatbot

bot = HarmonyChatbot()

# Chat with user
response = bot.chat("What is the weather?")
print(response)

# View conversation
bot.display_conversation()

# Export as JSON
json_data = bot.get_json_export()
print(json_data)
```

### Example 2: Advanced Chatbot with Config

```python
from chatbot_advanced import AdvancedHarmonyChatbot

bot = AdvancedHarmonyChatbot(config_file="config.json")

# Chat with reasoning
response, reasoning = bot.chat_with_reasoning("Tell me about AI")
print(f"Reasoning: {reasoning}")
print(f"Response: {response}")

# Get statistics
stats = bot.get_stats()
print(f"Total messages: {stats['total_messages']}")

# Export in Harmony format
harmony_output = bot.get_harmony_export()
print(harmony_output)
```

### Example 3: Chain of Thought

```python
bot = AdvancedHarmonyChatbot()

# Chat with CoT enabled
response, reasoning = bot.chat_with_reasoning("What is 5 * 7?")

# View all messages including CoT
bot.display_conversation(include_cot=True)
```

## API Reference

### HarmonyChatbot Class

#### Methods

- **`__init__(messages_file: str = "messages.json")`**
  - Initialize chatbot with message storage file

- **`chat(user_input: str) -> str`**
  - Process user input and return response

- **`add_user_message(text: str) -> None`**
  - Add user message to history

- **`add_assistant_message(text: str, channel: str = "final") -> None`**
  - Add assistant message with specified channel

- **`display_conversation() -> None`**
  - Print formatted conversation history

- **`get_json_export() -> str`**
  - Export messages as JSON string

- **`get_dummy_response(user_input: str) -> str`**
  - Generate dummy response for testing

### AdvancedHarmonyChatbot Class

#### Additional Methods

- **`__init__(config_file: str = "config.json", messages_file: str = "messages.json")`**
  - Initialize with configuration file support

- **`chat_with_reasoning(user_input: str) -> tuple[str, str]`**
  - Chat with chain-of-thought reasoning
  - Returns (response, reasoning)

- **`get_harmony_export() -> str`**
  - Export full conversation in Harmony format

- **`get_stats() -> Dict[str, Any]`**
  - Get conversation statistics

- **`display_conversation(include_cot: bool = False) -> None`**
  - Display history, optionally including CoT messages

## Configuration

### config.json Structure

```json
{
  "chatbot": {
    "name": "Harmony Chatbot",
    "version": "1.0.0",
    "description": "...",
    "knowledge_cutoff": "2024-06",
    "current_date": "2025-01-26",
    "reasoning": "high"
  },
  "messages_file": "messages.json",
  "system_prompt": {
    "role": "system",
    "content": "You are ChatGPT..."
  },
  "dummy_responses": {
    "hello": "Hello! How can I help?",
    "goodbye": "Goodbye!",
    "default": "You said: '{input}'"
  }
}
```

### Customization

1. **Change system prompt**: Edit `system_prompt.content` in config.json
2. **Add responses**: Add key-value pairs to `dummy_responses`
3. **Update metadata**: Change `knowledge_cutoff`, `current_date`, etc.

## Advanced Features

### 1. Chain of Thought (CoT)

Messages in the "analysis" channel are internal reasoning that won't be shown to users:

```python
bot.add_assistant_message(
    "Processing the calculation...",
    channel="analysis",
    is_cot=True
)
```

### 2. Harmony Format Export

Get the full conversation in Harmony format (suitable for gpt-oss APIs):

```python
harmony_format = bot.get_harmony_export()
# Can be sent directly to gpt-oss API
```

### 3. Conversation Statistics

```python
stats = bot.get_stats()
# Returns:
# {
#   "total_messages": 10,
#   "user_messages": 5,
#   "assistant_messages": 5,
#   "chain_of_thought_messages": 2,
#   "total_characters": 1234,
#   "config_name": "Harmony Chatbot"
# }
```

### 4. Multiple Export Formats

```python
# JSON format
json_export = bot.get_json_export()

# Harmony format
harmony_export = bot.get_harmony_export()

# Statistics
stats = bot.get_stats()
```

## Integration with Real APIs

To integrate with actual OpenAI gpt-oss API:

1. Replace `get_dummy_response()` with actual API calls
2. Parse Harmony format responses
3. Maintain message history for context
4. Use `get_harmony_export()` to format input for API

Example stub:

```python
def get_real_response(self, user_input: str) -> str:
    harmony_context = self.get_harmony_export()
    
    # Call gpt-oss API with harmony_context
    response = openai_api.create_completion(
        prompt=harmony_context,
        model="gpt-oss"
    )
    
    return response.text
```

## Interactive Commands

When running the chatbot interactively:

- **Normal text**: Send chat message
- `show`: Display conversation history
- `show-cot`: Include chain-of-thought messages
- `harmony`: Show Harmony format output
- `export`: Export as JSON
- `stats`: Show conversation statistics
- `quit`: Exit chatbot

## Tips & Best Practices

1. **Always use channels**: Specify appropriate channel (final, analysis, commentary)
2. **Preserve CoT**: Don't remove analysis messages from subsequent API calls
3. **Clean exports**: Use JSON for storage, Harmony format for API calls
4. **System messages**: Define clear system prompts in config
5. **Error handling**: Always check for invalid user input

## Troubleshooting

- **Messages not saving**: Check file permissions for `messages.json`
- **Config not loading**: Ensure `config.json` is in working directory
- **Harmony format issues**: Verify special tokens are properly enclosed
- **Channel errors**: Use only "final", "analysis", or "commentary"

## References

- [OpenAI Harmony Format Documentation](https://platform.openai.com/docs/harmony)
- [gpt-oss Model Documentation](https://github.com/openai/gpt-oss)
- [JSON Schema Specification](https://json-schema.org/)

---

**Last Updated**: 2025-01-26  
**Version**: 1.0.0
