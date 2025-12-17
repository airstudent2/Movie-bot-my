
#!/bin/bash
python -m bot.main &
exec gunicorn server.app:app --bind 0.0.0.0:$PORT --timeout 120
