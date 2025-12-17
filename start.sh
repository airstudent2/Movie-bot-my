
#!/bin/bash

# 1. Bot start করো ব্যাকগ্রাউন্ডে (& চিহ্ন খুব জরুরি)
python -m bot.main &

# 2. Flask Server start করো
gunicorn server.app:app --bind 0.0.0.0:$PORT
