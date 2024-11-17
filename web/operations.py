from typing import Optional
from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import Session, declarative_base
from sqlalchemy.exc import IntegrityError
from pydantic import BaseModel, EmailStr


class NotFoundError(Exception):
    pass

class ValidationError(Exception):
    pass


class User(BaseModel):
    id: int
    first_name: str
    last_name: str
    email: EmailStr


class UserCreate(BaseModel):
    first_name: str
    last_name: str
    email: EmailStr


class UserUpdate(BaseModel):
    first_name: Optional[str]
    last_name: Optional[str]
    email: Optional[EmailStr]


Base = declarative_base()


class DBUser(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    first_name = Column(String, nullable=False)
    last_name = Column(String, nullable=False)
    email = Column(String, unique=True, nullable=False)


def db_list_users(db: Session) -> list[User]:
    db_users = db.query(DBUser).all()
    return [User(**user.__dict__) for user in db_users]

def db_find_user(user_id: int, db: Session) -> DBUser:
    db_user = db.query(DBUser).filter(DBUser.id == user_id).first()
    if db_user is None:
        raise NotFoundError()
    return db_user


def db_create_user(user: UserCreate, session: Session) -> User:
    db_user = DBUser(**user.dict())
    try:
        session.add(db_user)
        session.commit()
        session.refresh(db_user)
    except IntegrityError:
        session.rollback()
        raise ValidationError("Email already exists")
    return User(**db_user.__dict__)


def db_read_user(user_id: int, session: Session) -> User:
    db_user = db_find_user(user_id, session)
    return User(**db_user.__dict__)


def db_update_user(user_id: int, user: UserUpdate, session: Session) -> User:
    db_user = db_find_user(user_id, session)

    for key, value in user.__dict__.items():
        setattr(db_user, key, value)

    session.commit()
    session.refresh(db_user)

    return User(**db_user.__dict__)


def db_delete_user(user_id: int, session: Session) -> User:
    db_user = db_find_user(user_id, session)
    session.delete(db_user)
    session.commit()
    return User(**db_user.__dict__)
