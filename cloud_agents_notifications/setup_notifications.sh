#!/bin/bash
# Quick setup script for Cloud Agents Notifications

echo "Cloud Agents Notification Service Setup"
echo "======================================"

# Check Python
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 not found. Please install Python 3.8+"
    exit 1
fi

echo "✓ Python found: $(python3 --version)"

# Create virtual environment
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
source venv/bin/activate

# Install dependencies
echo "Installing dependencies..."
pip install -r requirements.txt

echo ""
echo "✓ Setup complete!"
echo ""
echo "Next steps:"
echo "1. Configure notification channels (see README.md):"
echo "   - Discord: export DISCORD_WEBHOOK_URL='...'"
echo "   - Slack: export SLACK_WEBHOOK_URL='...'"
echo "   - SMS: export TWILIO_ACCOUNT_SID='...' (and others)"
echo ""
echo "2. Start the service:"
echo "   source venv/bin/activate"
echo "   python notification_service.py"
echo ""
echo "3. For local testing, use ngrok:"
echo "   ngrok http 8001"
echo ""
echo "4. Use the webhook URL when launching Cloud Agents"
