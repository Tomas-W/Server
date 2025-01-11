import os

from src import get_app


if __name__ == "__main__":
    env = os.environ.get("FLASK_ENV", "debug").lower()
    debug_mode = env == "debug"
    
    app = get_app()
    port = int(os.environ.get("PORT", 5000))
    
    # Only log if we're not in the reloader
    if not os.environ.get('WERKZEUG_RUN_MAIN'):
        if debug_mode:
            app.logger.warning("Running in debug mode - USE WITH CAUTION!")
        else:
            app.logger.info("Running in production mode with platform SSL")
    
    app.run(
        host="0.0.0.0",
        port=port,
        debug=debug_mode
    )
