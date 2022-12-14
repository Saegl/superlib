import math

from fastapi import FastAPI, Request, Form, status, Cookie, Depends, Query
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from tortoise.exceptions import DoesNotExist, OperationalError
from tortoise.contrib.fastapi import register_tortoise
from passlib.context import CryptContext

from app.models import User, Author, Book, Publisher

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
async def get_user(userid: str = Cookie(default="-1")) -> User | None:
    try:
        user = await User.get(id=userid)
        return user
    except DoesNotExist:
        pass
    except OperationalError:  # incorrect UUID
        pass


################### Routers
@app.get("/", response_class=HTMLResponse)
async def index(
    request: Request, user: User = Depends(get_user), page: int = Query(default=1)
):
    offset = (page - 1) * 16
    books = await Book.all().offset(offset).limit(16).order_by("-created_at")
    books_count = await Book.all().count()
    pages_count = math.ceil(books_count / 16)

    first_page = max(page - 5, 1)
    last_page = min(first_page + 10, pages_count) + 1
    pages = list(range(first_page, last_page))

    return templates.TemplateResponse(
        "index.html",
        {
            "request": request,
            "user": user,
            "books": books,
            "current_page": page,
            "pages": pages,
        },
    )


@app.get("/about", response_class=HTMLResponse)
async def about(request: Request, user: User = Depends(get_user)):
    return templates.TemplateResponse("about.html", {"request": request, "user": user})


@app.get("/contact", response_class=HTMLResponse)
async def contact(request: Request, user: User = Depends(get_user)):
    return templates.TemplateResponse(
        "contact.html", {"request": request, "user": user}
    )


@app.get("/book/{isbn}", response_class=HTMLResponse)
async def book(request: Request, isbn: str, user: User = Depends(get_user)):
    book = await Book.get(isbn=isbn)
    book.views += 1
    # book.created_at = book.created_at
    await book.save()
    return templates.TemplateResponse(
        "book-detail.html",
        {
            "request": request,
            "user": user,
            "book": book,
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


@app.post("/gendata")
async def gendata():
    from faker import Faker
    from random import randint

    fake = Faker()

    for _ in range(100):
        name, surname = fake.name().split(maxsplit=1)
        author = await Author.create(
            name=name,
            surname=surname,
            bio=fake.text(),
            email=fake.email(),
            password_hash="1234",
        )

        publisher = await Publisher.create(
            name=fake.company(),
        )

        for _ in range(10):
            await Book.create(
                isbn=fake.isbn13(),
                author=author,
                title=fake.sentence(),
                image_url=f"https://placekitten.com/{randint(400, 600)}/{randint(600, 800)}",
                publisher=publisher,
                year=fake.year(),
                pages=randint(50, 1000),
                views=0,
            )

    return {"status": "Success"}


app.mount(
    "/",
    StaticFiles(
        directory="static",
        html=True,
    ),
    name="static",
)
