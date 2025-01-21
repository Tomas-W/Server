import os

from dotenv import load_dotenv
load_dotenv('.flaskenv')

from src import get_app


if __name__ == "__main__":
    env = os.environ.get("FLASK_ENV", "debug").lower()
    debug_mode = env == "debug"
    
    app = get_app()
    port = int(os.environ.get("PORT", 5000))
    
    app.run(
        host="0.0.0.0",
        port=port,
        debug=debug_mode
    )
