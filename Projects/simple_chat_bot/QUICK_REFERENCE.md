# Harmony Chatbot - Quick Reference Card

## Quick Start

```bash
# Run interactive chatbot
python3 chatbot.py

# Run advanced version with config
python3 chatbot_advanced.py

# View all demos
python3 demo.py

# Run interactive menu
bash quickstart.sh
```

## Basic Usage

```python
from chatbot import HarmonyChatbot

bot = HarmonyChatbot()
response = bot.chat("Your message here")
bot.display_conversation()
print(bot.get_json_export())
```

## Advanced Usage

```python
from chatbot_advanced import AdvancedHarmonyChatbot

bot = AdvancedHarmonyChatbot()

# Chat with reasoning
response, reasoning = bot.chat_with_reasoning("Your question")

# Get statistics
stats = bot.get_stats()

# Export formats
json_export = bot.get_json_export()
harmony_export = bot.get_harmony_export()
```

## Harmony Format Examples

### Basic Message Structure
```
<|start|>{header}<|message|>{content}<|end|>
```

### With Channel
```
<|start|><|channel|>final user<|message|>What is 2+2?<|end|>
```

### All Roles
```
# System
<|start|><|channel|>final system<|message|>You are helpful.<|end|>

# User
<|start|><|channel|>final user<|message|>Ask a question<|end|>

# Assistant
<|start|><|channel|>final assistant<|message|>Give a response<|end|>
```

## Special Tokens

| Token | Meaning |
|-------|---------|
| `<|start|>` | Begin message |
| `<|end|>` | End message |
| `<|message|>` | Header separator |
| `<|channel|>` | Set channel |
| `<|constrain|>` | Type constraint |
| `<|return|>` | Completion end |
| `<|call|>` | Tool call |

## Message Channels

| Channel | Purpose |
|---------|---------|
| **final** | User-facing responses |
| **analysis** | Chain-of-thought (internal) |
| **commentary** | Preambles, tool calls |

## Interactive Commands

When running chatbot:
- Type normally to chat
- `show` - View conversation history
- `show-cot` - Show with chain-of-thought
- `harmony` - Show Harmony format
- `export` - Export as JSON
- `stats` - Show statistics
- `quit` - Exit

## JSON Message Format

```json
{
  "role": "user|assistant|system",
  "content": "Message text",
  "channel": "final|analysis|commentary",
  "timestamp": "2025-01-26T12:34:56.789123",
  "is_chain_of_thought": false,
  "harmony_format": "<|start|>..."
}
```

## Key Methods

### HarmonyChatbot
- `chat(input)` - Chat and get response
- `add_user_message(text)` - Add user message
- `add_assistant_message(text, channel)` - Add response
- `display_conversation()` - Show history
- `get_json_export()` - Export as JSON
- `get_dummy_response(input)` - Get dummy response

### AdvancedHarmonyChatbot (adds)
- `chat_with_reasoning(input)` - Chat + reasoning
- `get_harmony_export()` - Export in Harmony format
- `get_stats()` - Get statistics
- `display_conversation(include_cot)` - Show history

## Configuration

Edit `config.json`:

```json
{
  "chatbot": {
    "name": "Your Bot",
    "reasoning": "high"
  },
  "dummy_responses": {
    "hello": "Your response",
    "default": "Default response"
  },
  "system_prompt": {
    "content": "Your system prompt"
  }
}
```

## File Locations

| File | Purpose |
|------|---------|
| `chatbot.py` | Basic implementation |
| `chatbot_advanced.py` | Advanced features |
| `config.json` | Configuration |
| `messages.json` | Message storage |
| `demo.py` | Feature demos |
| `test_chatbot.py` | Tests |
| `README.md` | Quick start |
| `GUIDE.md` | Full documentation |

## Common Tasks

### Get full conversation
```python
bot.display_conversation()
```

### Get conversation with reasoning
```python
bot.display_conversation(include_cot=True)
```

### Export for API
```python
harmony_text = bot.get_harmony_export()
```

### Clear messages
```python
bot.messages = []
bot._save_messages()
```

### Add custom response
```python
bot.add_assistant_message("Custom response", channel="final")
```

### Get chat statistics
```python
stats = bot.get_stats()
print(f"Total: {stats['total_messages']}")
```

## Harmony Format Quick Guide

**Key Rules:**
1. Every message starts with `<|start|>` and ends with `<|end|>`
2. Header comes first, then `<|message|>`, then content
3. Always specify channel: `<|channel|>final`, `<|channel|>analysis`, etc.
4. Roles: system, user, assistant
5. Special tokens are literal strings (not replaced)

**Minimal Example:**
```
<|start|>user<|message|>Hello<|end|>
<|start|>assistant<|channel|>final<|message|>Hi!<|end|>
```

## Troubleshooting

| Issue | Solution |
|-------|----------|
| Messages not saving | Check file permissions |
| Config not loading | Ensure config.json exists |
| JSON parse error | Verify JSON syntax |
| No responses | Check dummy_responses config |
| Import error | Ensure .py files in same directory |

## Tips

- Always include channel in headers
- Use "final" for user responses
- Preserve analysis messages for APIs
- Timestamps are automatic
- Config changes take effect on next run
- JSON is human-readable
- Export often for backup

## Related Resources

- [Harmony Format Docs](https://example.com/harmony)
- [OpenAI API](https://platform.openai.com)
- [Python JSON](https://docs.python.org/3/library/json.html)
- [ISO 8601](https://en.wikipedia.org/wiki/ISO_8601)

---

**Quick Command Reference:**
```bash
python3 chatbot.py              # Start chatbot
python3 chatbot_advanced.py     # Advanced mode
python3 demo.py                 # See demos
python3 -m pytest test_chatbot.py -v  # Run tests
```

**Python Imports:**
```python
from chatbot import HarmonyChatbot
from chatbot_advanced import AdvancedHarmonyChatbot
```

**Next Steps:**
1. Read [GUIDE.md](./GUIDE.md) for full documentation
2. Run [demo.py](./demo.py) to see features
3. Check [config.json](./config.json) to customize
4. Review [chatbot_advanced.py](./chatbot_advanced.py) source code
