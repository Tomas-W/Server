from src import get_app


if __name__ == "__main__":
    app = get_app()
    app.run(host="0.0.0.0", port=5000)  # host="0.0.0.0"
