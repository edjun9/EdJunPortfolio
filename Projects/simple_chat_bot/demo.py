#!/usr/bin/env python3
"""
Demo script showing various chatbot features and Harmony format examples.
"""

from chatbot_advanced import AdvancedHarmonyChatbot
import json


def demo_basic_conversation():
    """Demo 1: Basic conversation with message storage."""
    print("\n" + "="*70)
    print("DEMO 1: Basic Conversation with JSON Storage")
    print("="*70)
    
    # Clear messages for clean demo
    bot = AdvancedHarmonyChatbot()
    bot.messages = []
    bot._save_messages()
    
    # Have a simple conversation
    conversations = [
        "hello",
        "how are you",
        "what is harmony",
    ]
    
    for user_msg in conversations:
        response = bot.chat(user_msg)
        print(f"User: {user_msg}")
        print(f"Bot:  {response}\n")
    
    # Show stored JSON
    print("Stored Messages (JSON):")
    print("-" * 70)
    data = json.loads(bot.get_json_export())
    for msg in data[-3:]:  # Show last 3 messages
        print(json.dumps(msg, indent=2))
    print("-" * 70)


def demo_harmony_format():
    """Demo 2: Show Harmony format structure."""
    print("\n" + "="*70)
    print("DEMO 2: Harmony Format Structure")
    print("="*70)
    
    bot = AdvancedHarmonyChatbot()
    
    # Show system message in Harmony format
    system_prompt = bot.config.get("system_prompt", {})
    system_content = system_prompt.get("content", "")
    harmony_msg = bot._format_message("system", system_content[:50] + "...")
    
    print("\nSystem Message in Harmony Format:")
    print(harmony_msg)
    
    # Show user message
    user_harmony = bot._format_message("user", "What is harmony?")
    print("\nUser Message in Harmony Format:")
    print(user_harmony)
    
    # Show assistant message with channel
    assistant_harmony = bot._format_message(
        "assistant",
        "Harmony is the response format for gpt-oss models.",
        channel="final"
    )
    print("\nAssistant Message in Harmony Format:")
    print(assistant_harmony)
    
    print("\nSpecial Tokens Used:")
    for token_name, token_value in bot.SPECIAL_TOKENS.items():
        print(f"  {token_name}: {token_value}")


def demo_channels():
    """Demo 3: Show different message channels."""
    print("\n" + "="*70)
    print("DEMO 3: Message Channels (final, analysis, commentary)")
    print("="*70)
    
    bot = AdvancedHarmonyChatbot()
    bot.messages = []
    
    # Add messages with different channels
    channels_demo = [
        ("analysis", "This is internal chain-of-thought, not shown to users"),
        ("commentary", "This is for preambles or action plans"),
        ("final", "This is the actual response shown to the user"),
    ]
    
    for channel, description in channels_demo:
        msg = {
            "role": "assistant",
            "content": description,
            "channel": channel,
            "timestamp": "2026-01-26T00:00:00",
        }
        bot.messages.append(msg)
    
    print("\nChannel Demonstrations:")
    for i, (channel, desc) in enumerate(channels_demo, 1):
        print(f"\n{i}. Channel: {channel}")
        print(f"   Purpose: {desc}")
        print(f"   Harmony: {bot._format_message('assistant', desc[:30] + '...', channel=channel)}")


def demo_statistics():
    """Demo 4: Conversation statistics."""
    print("\n" + "="*70)
    print("DEMO 4: Conversation Statistics")
    print("="*70)
    
    bot = AdvancedHarmonyChatbot()
    
    if not bot.messages:
        print("\nNo messages in history. Adding sample messages...")
        for i in range(5):
            bot.add_user_message(f"Sample message {i+1}")
            bot.add_assistant_message(f"Response {i+1}")
    
    stats = bot.get_stats()
    print("\nConversation Statistics:")
    for key, value in stats.items():
        print(f"  • {key}: {value}")


def demo_chain_of_thought():
    """Demo 5: Chain of thought reasoning."""
    print("\n" + "="*70)
    print("DEMO 5: Chain of Thought (CoT) Reasoning")
    print("="*70)
    
    bot = AdvancedHarmonyChatbot()
    bot.messages = []
    
    # Add conversation with reasoning
    print("\nUser: What is 2+2?")
    response, reasoning = bot.chat_with_reasoning("What is 2+2?")
    print(f"Internal Reasoning: {reasoning}")
    print(f"Final Response: {response}")
    
    # Show all messages including CoT
    print("\nAll Messages (including Chain-of-Thought):")
    for msg in bot.messages:
        is_cot = msg.get("is_chain_of_thought", False)
        cot_label = " [CHAIN-OF-THOUGHT]" if is_cot else ""
        print(f"  {msg['role'].upper()}: {msg['content']}{cot_label}")


def demo_export_formats():
    """Demo 6: Different export formats."""
    print("\n" + "="*70)
    print("DEMO 6: Export Formats")
    print("="*70)
    
    bot = AdvancedHarmonyChatbot()
    
    if not bot.messages:
        bot.add_user_message("Hello!")
        bot.add_assistant_message("Hi there!")
    
    # JSON Export
    print("\nJSON Export (first message):")
    json_data = json.loads(bot.get_json_export())
    if json_data:
        print(json.dumps(json_data[0], indent=2))
    
    # Harmony Format Export (first few lines)
    print("\nHarmony Format Export (first 200 chars):")
    harmony_export = bot.get_harmony_export()
    print(harmony_export[:200] + "...")


def run_all_demos():
    """Run all demo functions."""
    print("\n")
    print("╔" + "="*68 + "╗")
    print("║" + " "*15 + "HARMONY CHATBOT DEMOS" + " "*33 + "║")
    print("╚" + "="*68 + "╝")
    
    demos = [
        ("Basic Conversation", demo_basic_conversation),
        ("Harmony Format", demo_harmony_format),
        ("Message Channels", demo_channels),
        ("Statistics", demo_statistics),
        ("Chain of Thought", demo_chain_of_thought),
        ("Export Formats", demo_export_formats),
    ]
    
    for i, (name, func) in enumerate(demos, 1):
        try:
            func()
        except Exception as e:
            print(f"\nError in {name}: {e}")
    
    print("\n" + "="*70)
    print("All demos completed!")
    print("="*70 + "\n")


if __name__ == "__main__":
    run_all_demos()
