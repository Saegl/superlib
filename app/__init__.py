from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from tortoise.contrib.fastapi import register_tortoise
from app.models import User

################### Settings
APP_URL = "postgres://demo:demo@localhost:5432/superlib"

app = FastAPI(
    title="SuperLib",
    description="Websystem for sharing both physical and electronic books",
    version="0.1.0",
)
register_tortoise(
    app,
    db_url=APP_URL,
    modules={"models": ["app.models"]},
    generate_schemas=True,
)
templates = Jinja2Templates(directory="templates")

################### Routers
@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


@app.get("/about", response_class=HTMLResponse)
async def about(request: Request):
    return templates.TemplateResponse("about.html", {"request": request})


@app.get("/contact", response_class=HTMLResponse)
async def contact(request: Request):
    return templates.TemplateResponse("contact.html", {"request": request})


@app.get("/book/{id}", response_class=HTMLResponse)
async def book(request: Request):
    return templates.TemplateResponse(
        "book-detail.html",
        {
            "request": request,
            "title": "The Computer Science book",
        },
    )


@app.get("/signin", response_class=HTMLResponse)
async def signin(request: Request):
    return templates.TemplateResponse("signin.html", {"request": request})


@app.post("/signin")
async def signin(
    email: str = Form(),
    password: str = Form(),
):
    return {
        "email": email,
        "password": password,
    }


@app.get("/signup", response_class=HTMLResponse)
async def signup(request: Request):
    return templates.TemplateResponse("signup.html", {"request": request})


@app.post("/signup")
async def signin(
    name: str = Form(),
    surname: str = Form(),
    email: str = Form(),
    bio: str = Form(),
):
    return {
        "name": name,
        "surname": surname,
        "email": email,
        "bio": bio,
    }


@app.post("/register")
async def register():
    user = await User.create(
        name="Alisher",
        surname="Zhubanyshev",
        email="zhubanysh.alisher@gmail.com",
        password_hash="1234",
    )
    return {"message": user.name}


app.mount(
    "/",
    StaticFiles(
        directory="static",
        html=True,
    ),
    name="static",
)
