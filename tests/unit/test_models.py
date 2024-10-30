from src.models.auth_model.auth_mod import User
from tests.settings import correct_user_data, false_user_data
from src.auth.auth_forms import RegistrationForm

def test_new_user() -> None:
    """
    GIVEN a User model
    WHEN a new User is created
    THEN check the email, username, password_hash, and role fields are defined correctly
    """
    user = User(email="test@example.com", username="testuser", password_hash="hashed_password", role="user")
    assert user.email == "test@example.com"
    assert user.username == "testuser"
    assert user.password_hash == "hashed_password"


def test_registration_form_validation():
    """
    GIVEN registration form data
    WHEN the form is validated
    THEN check for appropriate validation errors
    """
    for key, data in false_user_data.items():
        form = RegistrationForm(
            email=data['email'],
            username=data['username'],
            password=data['password'],
            password2=data['password'],
            fast_name=data['fast_name'],
            fast_code=data['fast_code'],
        )
        
        assert not form.validate()
        
        if key == 'false1':
            assert 'email' in form.errors
            assert 'Invalid email address' in form.errors['email']
        elif key == 'false2':
            assert 'username' in form.errors
            assert 'Username must be at least 2 characters long' in form.errors['username']
        elif key == 'false3':
            assert 'password' in form.errors
            assert 'Password must be at least 8 characters long' in form.errors['password']
        elif key == 'false4':
            assert 'password' in form.errors
            assert 'Password must be at most 20 characters long' in form.errors['password']
        elif key == 'false5':
            assert 'password' in form.errors
            assert 'Password must contain at least one uppercase letter' in form.errors['password']
        elif key == 'false6':
            assert 'password' in form.errors
            assert 'Password must contain at least one lowercase letter' in form.errors['password']
        elif key == 'false7':
            assert 'password' in form.errors
            assert 'Password must contain at least one special character' in form.errors['password']
        elif key == 'false8':
            assert 'fast_name' in form.errors
            assert 'Fast name must be at least 2 characters long' in form.errors['fast_name']
        elif key == 'false9':
            assert 'fast_code' in form.errors
            assert 'Fast code must be exactly 5 digits' in form.errors['fast_code']
        elif key == 'false10':
            assert 'fast_code' in form.errors
            assert 'Fast code must contain only digits' in form.errors['fast_code']

def test_correct_registration_form():
    """
    GIVEN correct registration form data
    WHEN the form is validated
    THEN check that validation passes
    """
    for key, data in user_data.items():
        form = RegistrationForm(
            email=data['email'],
            username=data['username'],
            password=data['password'],
            password2=data['password'],  # Assuming you have a password confirmation field
            fast_name=data['fast_name'],
            fast_code=data['fast_code']
        )
        
        assert form.validate(), f"Form validation failed for {key}: {form.errors}"
