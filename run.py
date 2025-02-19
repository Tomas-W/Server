import os
import logging


if os.environ.get("FLASK_ENV") != "deploy":
    from dotenv import load_dotenv
    load_dotenv('.env')
    load_dotenv('.flaskenv')


# Only disable Flask/Werkzeug logs
logging.getLogger("werkzeug").disabled = True
logging.getLogger("gunicorn.access").disabled = True

from src import get_app
app = get_app()

if __name__ == "__main__":
    env = os.environ.get("FLASK_ENV", "debug").lower()
    debug_mode = env == "debug"
    port = int(os.environ.get("PORT", 8080))
    
    app.run(
        host="0.0.0.0",
        port=port,
        debug=debug_mode
    )
