import os
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, Form, Depends, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from operations import (
    Base,
    UserCreate,
    UserUpdate,
    NotFoundError,
    db_create_user,
    db_delete_user,
    db_read_user,
    db_update_user,
    db_list_users,
)
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from starlette.status import HTTP_303_SEE_OTHER

DB_HOST = os.getenv("DB_HOST", "db")
DB_PORT = os.getenv("DB_PORT", 5432)
DB_NAME = os.getenv("DB_NAME")
DB_USER = os.getenv("DB_USER", "postgres")
DB_PASSWORD = os.getenv("DB_PASSWORD")

DATABASE_URL = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autoflush=False, autocommit=False, bind=engine)


@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


app = FastAPI(lifespan=lifespan)
templates = Jinja2Templates(directory="templates")


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.get("/", response_class=HTMLResponse)
@app.get("/users", response_class=HTMLResponse)
def list_users(request: Request, db: Session = Depends(get_db)) -> HTMLResponse:
    users = db_list_users(db)
    return templates.TemplateResponse("index.html", {"request": request, "users": users})


@app.get("/users/create", response_class=HTMLResponse)
def create_user_form(request: Request):
    return templates.TemplateResponse("create.html", {"request": request})


@app.post("/users")
def create_user(
        request: Request,
        first_name: str = Form(...),
        last_name: str = Form(...),
        email: str = Form(...),
        db: Session = Depends(get_db)
) -> RedirectResponse:
    user = UserCreate(first_name=first_name, last_name=last_name, email=email)
    db_create_user(user, db)
    return RedirectResponse(url="/users", status_code=HTTP_303_SEE_OTHER)


@app.get("/users/{user_id}")
def read_user(request: Request, user_id: int, db: Session = Depends(get_db)) -> HTMLResponse:
    try:
        user = db_read_user(user_id, db)
        return templates.TemplateResponse("view.html", {"user": user})
    except NotFoundError:
        raise HTTPException(status_code=404, detail="User not found")


@app.get("/users/{user_id}/edit", response_class=HTMLResponse)
def edit_user_form(request: Request, user_id: int, db: Session = Depends(get_db)):
    user = db_read_user(user_id, db)
    return templates.TemplateResponse("edit.html", {"request": request, "user": user})


@app.post("/users/{user_id}")
def update_item(
        request: Request,
        user_id: int,
        first_name: str = Form(...),
        last_name: str = Form(...),
        email: str = Form(...),
        db: Session = Depends(get_db)
) -> RedirectResponse:
    try:
        user = UserUpdate(first_name=first_name, last_name=last_name, email=email)
        db_update_user(user_id, user, db)
    except NotFoundError:
        raise HTTPException(status_code=404, detail="User not found")
    finally:
        return RedirectResponse(url="/users", status_code=HTTP_303_SEE_OTHER)


@app.post("/users/{user_id}/delete")
def delete_user(request: Request, user_id: int, db: Session = Depends(get_db)) -> RedirectResponse:
    try:
        db_delete_user(user_id, db)
    except NotFoundError:
        raise HTTPException(status_code=404, detail="User not found")
    finally:
        return RedirectResponse(url="/users", status_code=HTTP_303_SEE_OTHER)
