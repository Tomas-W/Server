import pytest
import sys
import os


from src import get_app, server_db_

@pytest.fixture()
def app():
    app = get_app(testing=True)
    
    with app.app_context():
        server_db_.create_all()
        
    yield app

@pytest.fixture()
def client(app):
    return app.test_client()

# Add this print statement for debugging
print("conftest.py loaded")

