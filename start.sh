#!/bin/bash

echo "🚀 Starting Movie Nest Bot System..."

# Start Telegram Bot
echo "🤖 Starting Telegram Bot..."
python -m bot.main &

# Give bot time to start
sleep 5

# Start Flask Server
echo "🌐 Starting Flask Server..."
exec gunicorn server.app:app --bind 0.0.0.0:${PORT:-10000}
