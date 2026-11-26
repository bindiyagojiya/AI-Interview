import pytest
from fastapi import HTTPException
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.db.base import Base
from app.models.user import User
from app.models.profile import Profile
from app.schemas.user import UserCreate, UserLogin
from app.core.security import verify_password, get_password_hash, create_access_token
from app.api.v1.endpoints.auth import register, login

# In-memory SQLite session fixture for isolated auth testing
@pytest.fixture
def db_session():
    engine = create_engine("sqlite:///:memory:", connect_args={"check_same_thread": False})
    Base.metadata.create_all(bind=engine)
    Session = sessionmaker(bind=engine)
    session = Session()
    try:
        yield session
    finally:
        session.close()

def test_password_hashing_and_token():
    password = "SecurePassword123"
    hashed = get_password_hash(password)
    assert hashed != password
    assert verify_password(password, hashed) is True
    assert verify_password("WrongPassword", hashed) is False

    token = create_access_token(subject="1")
    assert isinstance(token, str)
    assert len(token) > 20

def test_user_registration_and_login(db_session):
    # 1. Register a new student
    user_in = UserCreate(
        email="student@example.com",
        full_name="Alex Student",
        password="MySecretPassword"
    )
    user = register(user_in=user_in, db=db_session)
    assert user.id is not None
    assert user.email == "student@example.com"
    assert user.full_name == "Alex Student"
    assert user.profile is not None
    assert user.profile.target_role == "Software Engineer"

    # 2. Prevent duplicate email registration
    with pytest.raises(HTTPException) as exc_info:
        register(user_in=user_in, db=db_session)
    assert exc_info.value.status_code == 400
    assert "already exists" in exc_info.value.detail

    # 3. Successful login
    login_in = UserLogin(email="student@example.com", password="MySecretPassword")
    token_response = login(login_in=login_in, db=db_session)
    assert "access_token" in token_response
    assert token_response["token_type"] == "bearer"

    # 4. Failed login with incorrect password
    bad_login = UserLogin(email="student@example.com", password="IncorrectPassword")
    with pytest.raises(HTTPException) as exc_info:
        login(login_in=bad_login, db=db_session)
    assert exc_info.value.status_code == 401

