
#!/bin/bash

# Start Flask server in background
gunicorn server.app:app --bind 0.0.0.0:${PORT:-10000} &

# Start Telegram Bot
python -m bot.main
