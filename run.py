import os
from src import get_app

# Only load .flaskenv in development
if os.environ.get("FLASK_ENV") != "deploy":
    from dotenv import load_dotenv
    load_dotenv('.flaskenv')

app = get_app()

if __name__ == "__main__":
    env = os.environ.get("FLASK_ENV", "debug").lower()
    debug_mode = env == "debug"
    port = int(os.environ.get("PORT", 5000))
    
    app.run(
        host="0.0.0.0",
        port=port,
        debug=debug_mode
    )
