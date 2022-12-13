from fastapi import FastAPI, Request, Form, status, Cookie, Depends
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from tortoise.exceptions import DoesNotExist, OperationalError
from tortoise.contrib.fastapi import register_tortoise
from passlib.context import CryptContext

from app.models import User

################### Settings
APP_URL = "postgres://demo:demo@localhost:5432/superlib"
pwdctx = CryptContext(schemes=["bcrypt"], deprecated="auto")

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


################### Services
async def get_user(userid: str = Cookie()) -> User | None:
    try:
        user = await User.get(id=userid)
        return user
    except DoesNotExist:
        pass
    except OperationalError:  # incorrect UUID
        pass


################### Routers
@app.get("/", response_class=HTMLResponse)
async def index(request: Request, user: User = Depends(get_user)):
    return templates.TemplateResponse("index.html", {"request": request, "user": user})


@app.get("/about", response_class=HTMLResponse)
async def about(request: Request, user: User = Depends(get_user)):
    return templates.TemplateResponse("about.html", {"request": request, "user": user})


@app.get("/contact", response_class=HTMLResponse)
async def contact(request: Request, user: User = Depends(get_user)):
    return templates.TemplateResponse(
        "contact.html", {"request": request, "user": user}
    )


@app.get("/book/{id}", response_class=HTMLResponse)
async def book(request: Request, user: User = Depends(get_user)):
    return templates.TemplateResponse(
        "book-detail.html",
        {"request": request, "title": "The Computer Science book", "user": user},
    )


@app.get("/signin", response_class=HTMLResponse)
async def signin(request: Request):
    return templates.TemplateResponse("signin.html", {"request": request})


@app.post("/signin")
async def signin(
    email: str = Form(),
    password: str = Form(),
):
    try:
        user = await User.get(email=email)
        if pwdctx.verify(password, user.password_hash):
            # Correct password
            resp = RedirectResponse("/", status_code=status.HTTP_302_FOUND)
            resp.set_cookie("userid", user.id)
            return resp
        else:
            # Incorrect password
            return {"status": "Password incorrect"}
    except DoesNotExist:
        # Email not found
        return {"status": "Email not found"}


@app.get("/signup", response_class=HTMLResponse)
async def signup(request: Request):
    return templates.TemplateResponse("signup.html", {"request": request})


@app.post("/signup")
async def signin(
    name: str = Form(),
    surname: str = Form(),
    email: str = Form(),
    password: str = Form(),
    bio: str = Form(),
):
    user = await User.create(
        name=name,
        surname=surname,
        email=email,
        password_hash=pwdctx.hash(password),
        bio=bio,
    )
    resp = RedirectResponse("/", status_code=status.HTTP_302_FOUND)
    resp.set_cookie("userid", user.id)
    return resp


@app.get("/logout")
async def logout():
    resp = RedirectResponse("/", status_code=status.HTTP_302_FOUND)
    resp.set_cookie("userid", "-1")
    return resp


app.mount(
    "/",
    StaticFiles(
        directory="static",
        html=True,
    ),
    name="static",
)
