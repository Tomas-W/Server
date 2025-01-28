#!/bin/bash
PORT="${PORT:-8080}"
exec gunicorn run:app --bind "0.0.0.0:$PORT" --timeout 180 --workers 1 