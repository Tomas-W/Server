import os


if os.environ.get("FLASK_ENV") != "deploy":
    from dotenv import load_dotenv
    load_dotenv('.env')
    load_dotenv('.flaskenv')


from src import get_app
app = get_app()


if __name__ == "__main__":
    env = os.environ.get("FLASK_ENV", "debug").lower()
    debug_mode = env == "debug"
    port = int(os.environ.get("PORT", 5432))
    
    app.run(
        host="0.0.0.0",
        port=port,
        debug=debug_mode
    )
