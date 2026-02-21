#!/bin/bash
# Start bot in background
python bot.py &

# Start API server in foreground
uvicorn app.main:app --host 0.0.0.0 --port 3000
