from fastapi import FastAPI, Request, Form, Depends, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from starlette.status import HTTP_303_SEE_OTHER
from database import get_db
from models import User

app = FastAPI()
templates = Jinja2Templates(directory="templates")


@app.get("/", response_class=HTMLResponse)
@app.get("/users", response_class=HTMLResponse)
def list_users(request: Request, db: Session = Depends(get_db)):
    users = db.query(User).all()
    return templates.TemplateResponse("index.html", {"request": request, "users": users})


@app.get("/users/create", response_class=HTMLResponse)
def create_user_form(request: Request):
    return templates.TemplateResponse("create.html", {"request": request})


@app.post("/users", response_class=HTMLResponse)
def create_user(
        request: Request,
        first_name: str = Form(...),
        last_name: str = Form(...),
        email: str = Form(...),
        db: Session = Depends(get_db)
):
    new_user = User(first_name=first_name, last_name=last_name, email=email)
    db.add(new_user)
    try:
        db.commit()
        db.refresh(new_user)
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=400, detail="Email already exists")
    return RedirectResponse(url="/users", status_code=HTTP_303_SEE_OTHER)


@app.get("/users/{user_id}/edit", response_class=HTMLResponse)
def edit_user_form(request: Request, user_id: int, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return templates.TemplateResponse("edit.html", {"request": request, "user": user})


@app.post("/users/{user_id}", response_class=HTMLResponse)
def update_user(
        request: Request,
        user_id: int,
        first_name: str = Form(...),
        last_name: str = Form(...),
        email: str = Form(...),
        db: Session = Depends(get_db)
):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    user.first_name = first_name
    user.last_name = last_name
    user.email = email
    db.commit()
    return RedirectResponse(url="/users", status_code=HTTP_303_SEE_OTHER)


@app.get("/users/{user_id}", response_class=HTMLResponse)
def view_user(request: Request, user_id: int, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return templates.TemplateResponse("view.html", {"request": request, "user": user})


@app.post("/users/{user_id}/delete", response_class=HTMLResponse)
def delete_user(request: Request, user_id: int, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    db.delete(user)
    db.commit()
    return RedirectResponse(url="/users", status_code=HTTP_303_SEE_OTHER)
