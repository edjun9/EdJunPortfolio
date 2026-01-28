# Harmony Format Chatbot

A simple chatbot implementation using OpenAI's Harmony response format.

## Features

- **Harmony Format Compliance**: All messages are formatted according to the Harmony spec with special tokens (`<|start|>`, `<|end|>`, `<|message|>`, etc.)
- **JSON Message Storage**: Full conversation history stored in `messages.json`
- **Multi-channel Support**: Messages tracked with channels (final, analysis, commentary)
- **Persistent History**: Conversations are saved and can be reviewed

## Usage

```bash
python chatbot.py
```

### Commands

- **Normal chat**: Just type your message
- `show`: Display entire conversation history
- `export`: Export conversation as JSON
- `quit`: Exit the chatbot

## Example Interaction

```
You: hello
Bot: Hello! I'm a chatbot using Harmony format. How can I help you?

You: what is harmony
Bot: Harmony is the response format for gpt-oss models. It uses special tokens like <|start|>, <|end|>, and <|message|>.

You: show
[Displays full conversation with timestamps and Harmony formatting]

You: quit
Goodbye!
```

## Message Structure

Each message in `messages.json` contains:

```json
{
  "role": "user|assistant|system",
  "content": "Message text",
  "channel": "final|analysis|commentary",
  "timestamp": "ISO 8601 timestamp",
  "harmony_format": "Harmony formatted message"
}
```

## Harmony Format Example

User message:
```
<|start|>user<|message|>What is 2 + 2?<|end|>
```

Assistant response:
```
<|start|>assistant<|channel|>final<|message|>2 + 2 = 4.<|end|>
```

## Files

- `chatbot.py`: Main chatbot implementation
- `messages.json`: Conversation history storage
- `README.md`: This file

## Extending

To add real API integration:

1. Replace `get_dummy_response()` with actual OpenAI API calls
2. Parse Harmony format responses from the API
3. Store complete conversation with all metadata

## Notes

- Messages are automatically saved after each interaction
- The chatbot uses dummy responses for demonstration
- The Harmony format is preserved for all messages for compliance with the gpt-oss model specification
