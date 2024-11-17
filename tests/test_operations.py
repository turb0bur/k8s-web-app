import pytest
from fastapi.testclient import TestClient
from pydantic import ValidationError
from sqlalchemy import create_engine
from sqlalchemy.pool import StaticPool
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.exc import IntegrityError
from web.main import app, Base, get_db
from web.operations import (
    DBUser,
    UserCreate,
    UserUpdate,
    ValidationError as CustomValidationError,
    NotFoundError,
    db_list_users,
    db_create_user,
    db_read_user,
    db_find_user,
    db_update_user,
    db_delete_user,
)

client = TestClient(app)

DATABASE_URL = "sqlite:///:memory:"
engine = create_engine(
    DATABASE_URL,
    connect_args={
        "check_same_thread": False,
    },
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_db():
    database = TestingSessionLocal()
    yield database
    database.close()


app.dependency_overrides[get_db] = override_get_db


@pytest.fixture()
def session():
    Base.metadata.create_all(bind=engine)
    db_session = TestingSessionLocal()
    # db_item = DBUser(id=10, first_name="John", last_name="Doe", email="john_doe@mailinator.com")
    # db_session.add(db_item)
    # db_session.commit()
    yield db_session
    db_session.close()
    Base.metadata.drop_all(bind=engine)


def test_create_user_with_valid_data(session: Session):
    user = UserCreate(first_name="Jane", last_name="Doe", email="janedoe@example.com")
    db_user = db_create_user(user, session)
    assert db_user.first_name == "Jane"
    assert db_user.last_name == "Doe"
    assert db_user.email == "janedoe@example.com"


def test_create_user_with_missing_first_name(session: Session):
    try:
        user = UserCreate(last_name="Doe", email="janedoe@example.com")
        db_create_user(user, session)
    except ValidationError as e:
        assert "first_name" in str(e)


def test_create_user_with_invalid_email(session: Session):
    try:
        user = UserCreate(first_name="Jane", last_name="Doe", email="invalid-email")
        db_create_user(user, session)
    except ValidationError as e:
        assert "email" in str(e)


def test_create_user_with_existing_email(session: Session):
    user1 = UserCreate(first_name="Jane", last_name="Doe", email="janedoe@example.com")
    db_create_user(user1, session)
    user2 = UserCreate(first_name="John", last_name="Smith", email="janedoe@example.com")
    try:
        db_create_user(user2, session)
    except CustomValidationError as e:
        assert "Email already exists" in str(e)


def test_db_find_user(session: Session):
    user = DBUser(first_name="Jane", last_name="Doe", email="janedoe@example.com")
    session.add(user)
    session.commit()

    found_user = db_find_user(user.id, session)
    assert found_user.first_name == "Jane"
    assert found_user.last_name == "Doe"
    assert found_user.email == "janedoe@example.com"


def test_db_find_user_not_found(session: Session):
    with pytest.raises(NotFoundError):
        db_find_user(999, session)


def test_db_list_users(session: Session):
    user1 = DBUser(first_name="Jane", last_name="Doe", email="janedoe@example.com")
    user2 = DBUser(first_name="John", last_name="Smith", email="johnsmith@example.com")
    session.add(user1)
    session.add(user2)
    session.commit()

    users = db_list_users(session)
    assert len(users) == 2
    assert users[0].first_name == "Jane"
    assert users[1].first_name == "John"


def test_db_read_user(session: Session):
    user = DBUser(first_name="Jane", last_name="Doe", email="janedoe@example.com")
    session.add(user)
    session.commit()

    read_user = db_read_user(user.id, session)
    assert read_user.first_name == "Jane"
    assert read_user.last_name == "Doe"
    assert read_user.email == "janedoe@example.com"


def test_db_update_user_with_valid_data(session: Session):
    user = DBUser(first_name="Jane", last_name="Doe", email="janedoe@example.com")
    session.add(user)
    session.commit()

    update_data = UserUpdate(first_name="Janet", last_name="Smith", email="janetsmith@example.com")
    updated_user = db_update_user(user.id, update_data, session)

    assert updated_user.first_name == "Janet"
    assert updated_user.last_name == "Smith"
    assert updated_user.email == "janetsmith@example.com"


def test_db_update_user_with_invalid_email(session: Session):
    user = DBUser(first_name="Jane", last_name="Doe", email="janedoe@example.com")
    session.add(user)
    session.commit()

    try:
        update_data = UserUpdate(first_name="Jane", last_name="Doe", email="invalid-email")
        db_update_user(user.id, update_data, session)
    except ValidationError as e:
        assert "email" in str(e)


def test_db_update_user_not_found(session: Session):
    update_data = UserUpdate(first_name="Janet", last_name="Smith", email="janetsmith@example.com")
    with pytest.raises(NotFoundError):
        db_update_user(999, update_data, session)


def test_db_update_user_with_existing_email(session: Session):
    user1 = DBUser(first_name="Jane", last_name="Doe", email="janedoe@example.com")
    user2 = DBUser(first_name="John", last_name="Smith", email="johnsmith@example.com")
    session.add(user1)
    session.add(user2)
    session.commit()

    update_data = UserUpdate(first_name="Jane", last_name="Doe", email="johnsmith@example.com")
    try:
        db_update_user(user1.id, update_data, session)
    except IntegrityError as e:
        print('test', e)
        assert "UNIQUE constraint failed" in str(e)


def test_db_delete_user_success(session: Session):
    user = DBUser(first_name="Jane", last_name="Doe", email="janedoe@example.com")
    session.add(user)
    session.commit()

    result = db_delete_user(user.id, session)
    assert result.first_name == "Jane"
    assert result.last_name == "Doe"
    assert result.email == "janedoe@example.com"

    with pytest.raises(NotFoundError):
        db_find_user(user.id, session)


def test_db_delete_user_not_found(session: Session):
    with pytest.raises(NotFoundError):
        db_delete_user(999, session)
