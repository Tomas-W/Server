def test_home_redirect_to_login(client):
    # Try to access /home
    response = client.get("/home")
    assert response.status_code == 302  # Check for redirect
    
    # Check if the redirect is to the login page
    assert "/login2" in response.location
    
    # Follow the redirect
    response = client.get(response.location)
    assert response.status_code == 200
    
    # Check for login page content (adjust based on your actual login page)
    assert b"login" in response.data.lower()


# def test_fast_login(client):
#     response = client.get("/login2")
#     assert response.status_code == 200
    
    # response = client.post("/login2", data={"form_type": "fast_login",
    #                                         "fast_name": "testing",
    #                                         "fast_code": "00000"})
    # assert response.status_code == 302  # Check for redirect
    # assert "/home" in response.location

    # # Follow the redirect
    # response = client.get(response.location)
    # assert response.status_code == 200
    