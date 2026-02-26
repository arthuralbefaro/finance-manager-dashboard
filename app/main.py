from fastapi import FastAPI, Depends, Form, Request, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from app.database import engine, SessionLocal
from app.models import Transaction, Base, User
from datetime import date
from app.auth import hash_password, verify_password

Base.metadata.create_all(bind=engine)

app = FastAPI()
templates = Jinja2Templates(directory="app/templates")

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.get("/", response_class=HTMLResponse)
def home(request: Request, db: Session = Depends(get_db)):
    transactions = db.query(Transaction).all()

    income = sum(t.amount for t in transactions if t.type == "income")
    expense = sum(t.amount for t in transactions if t.type == "expense")
    balance = income - expense

    return templates.TemplateResponse("dashboard.html", {
        "request": request,
        "transactions": transactions,
        "income": income,
        "expense": expense,
        "balance": balance,
        "labels": [], 
        "values": []
    })


@app.post("/add")
def add_transaction(
    description: str = Form(...),
    category: str = Form(...),
    amount: float = Form(...),
    type: str = Form(...),
    db: Session = Depends(get_db)
):
    transaction = Transaction(
        description=description,
        category=category,
        amount=amount,
        type=type,
        date=date.today()
    )
    db.add(transaction)
    db.commit()
    return RedirectResponse("/", status_code=303)


@app.get("/delete/{id}")
def delete_transaction(id: int, db: Session = Depends(get_db)):
    transaction = db.query(Transaction).filter(Transaction.id == id).first()
    if transaction:
        db.delete(transaction)
        db.commit()
    return RedirectResponse("/", status_code=303)

@app.get("/register", response_class=HTMLResponse)
def register_page(request: Request):
    return templates.TemplateResponse("register.html", {"request": request})

@app.post("/register")
def register(username: str = Form(...), password: str = Form(...), db: Session = Depends(get_db)):
    user_exists = db.query(User).filter(User.username == username).first()
    if user_exists:
        raise HTTPException(status_code=400, detail="Usuário já existe")
    
    new_user = User(
        username=username,
        password=hash_password(password)
    )

    db.add(new_user)
    db.commit()

    return RedirectResponse("/login", status_code=303)

@app.get("/login", response_class=HTMLResponse)
def login_page(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})

@app.post("/login")
def login(username: str = Form(...), password: str = Form(...), db: Session = Depends(get_db)):
    user = db.query(User).filter(User.username == username).first()

    if not user or not verify_password(password, user.password):
        raise HTTPException(status_code=400, detail="Login inválido")
    
    response = RedirectResponse("/", status_code=303)
    response.set_cookie(key="user_id", value=str(user.id))
    return response