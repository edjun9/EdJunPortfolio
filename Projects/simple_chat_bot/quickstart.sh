#!/bin/bash
# Quick start script for Harmony Format Chatbot

echo "╔════════════════════════════════════════════════════════════════╗"
echo "║          Harmony Format Chatbot - Quick Start                  ║"
echo "╚════════════════════════════════════════════════════════════════╝"
echo ""

# Check Python version
python_version=$(python3 --version 2>&1 | awk '{print $2}')
echo "✓ Python version: $python_version"
echo ""

# Check if required files exist
echo "Checking project files..."
files=("chatbot.py" "chatbot_advanced.py" "config.json" "README.md")

for file in "${files[@]}"; do
    if [ -f "$file" ]; then
        echo "  ✓ $file"
    else
        echo "  ✗ $file (missing)"
    fi
done
echo ""

# Menu
echo "Choose an option:"
echo ""
echo "1) Run basic chatbot"
echo "2) Run advanced chatbot with config"
echo "3) Run all demos"
echo "4) View documentation"
echo "5) Run tests (if available)"
echo "6) Exit"
echo ""

read -p "Enter your choice (1-6): " choice

case $choice in
    1)
        echo ""
        echo "Starting basic chatbot..."
        echo "─────────────────────────────────────────────────────────────────"
        python3 chatbot.py
        ;;
    2)
        echo ""
        echo "Starting advanced chatbot..."
        echo "─────────────────────────────────────────────────────────────────"
        python3 chatbot_advanced.py
        ;;
    3)
        echo ""
        echo "Running all demos..."
        echo "─────────────────────────────────────────────────────────────────"
        python3 demo.py
        ;;
    4)
        echo ""
        if command -v less &> /dev/null; then
            less README.md
        else
            cat README.md | head -100
            echo ""
            echo "(Run 'cat README.md' to see full documentation)"
        fi
        ;;
    5)
        echo ""
        if [ -f "test_chatbot.py" ]; then
            echo "Running tests..."
            python3 -m pytest test_chatbot.py -v
        else
            echo "No tests found. To create tests, add test_chatbot.py"
        fi
        ;;
    6)
        echo "Goodbye!"
        exit 0
        ;;
    *)
        echo "Invalid choice. Exiting."
        exit 1
        ;;
esac

echo ""
echo "─────────────────────────────────────────────────────────────────"
echo "Done! For more information, see README.md or GUIDE.md"
echo ""
