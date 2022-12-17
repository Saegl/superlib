import math
from functools import reduce

from fastapi import FastAPI, Request, Form, status, Cookie, Depends, Query
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from tortoise.expressions import Q
from tortoise.exceptions import DoesNotExist, OperationalError
from tortoise.contrib.fastapi import register_tortoise
from passlib.context import CryptContext

from app.models import (
    User,
    Author,
    Book,
    Publisher,
    Category,
    Comment,
    Feedback,
    DownloadSource,
    Notification,
)

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
        query = User.get(id=userid)
        # print(query.sql())
        user = await query
        return user
    except DoesNotExist:
        pass
    except OperationalError:  # incorrect UUID
        pass


async def get_notifications(user: User | None = Depends(get_user)) -> dict:
    if user:
        notifications = await Notification.filter(user=user)
        return {"notifications": notifications}
    else:
        return {}


################### Routers
@app.get("/", response_class=HTMLResponse)
async def index(
    request: Request,
    user: User | None = Depends(get_user),
    notifications: dict = Depends(get_notifications),
    page: int = Query(default=1),
    query: str = Query(default=""),
    category: str = Query(default="none"),
):
    offset = (page - 1) * 16
    books = Book.all().offset(offset).limit(16).order_by("-created_at")
    books_count = Book.all()

    if query:
        qs = []
        for word in query.split("-"):
            qs.append(Q(title__icontains=word))

        filters = reduce(lambda a, b: a | b, qs)
        books = books.filter(filters)
        books_count = books_count.filter(filters)

    if category != "none":
        books = books.filter(category__name=category)
        books_count = books_count.filter(category__name=category)

    books_count = books_count.count()

    # print(books.sql())
    # print(books_count.sql())

    books = await books
    books_count = await books_count

    pages_count = math.ceil(books_count / 16)

    first_page = max(page - 5, 1)
    last_page = min(first_page + 10, pages_count) + 1
    pages = list(range(first_page, last_page))

    categories_query = Category.all()
    categories = await categories_query
    # print(categories_query.sql())

    return templates.TemplateResponse(
        "index.html",
        {
            "request": request,
            "user": user,
            "nav_item": "Books",
            "books": books,
            # Paginator
            "current_page": page,
            "pages_count": pages_count,
            "pages": pages,
            # Category
            "categories": categories,
            "current_category": category,
        }
        | notifications,
    )


@app.get("/about", response_class=HTMLResponse)
async def about(
    request: Request,
    user: User = Depends(get_user),
    notifications: dict = Depends(get_notifications),
):
    return templates.TemplateResponse(
        "about.html",
        {
            "request": request,
            "user": user,
            "nav_item": "About",
        }
        | notifications,
    )


@app.get("/contact", response_class=HTMLResponse)
async def contact(
    request: Request,
    user: User = Depends(get_user),
    notifications: dict = Depends(get_notifications),
):
    return templates.TemplateResponse(
        "contact.html",
        {
            "request": request,
            "user": user,
            "nav_item": "Contact",
        }
        | notifications,
    )


@app.post("/contact")
async def send_feedback(
    request: Request,
    title: str = Form(),
    email: str = Form(),
    issue_type: str = Form(),
    message: str = Form(),
):
    await Feedback.create(
        title=title,
        email=email,
        issue_type=Feedback.issue_index(issue_type),
        message=message,
    )
    return templates.TemplateResponse("feedback.html", {"request": request})


@app.get("/book/{isbn}", response_class=HTMLResponse)
async def book(
    request: Request,
    isbn: str,
    user: User = Depends(get_user),
    notifications: dict = Depends(get_notifications),
):
    # print(Book.get(isbn=isbn).sql())
    book = await Book.get(isbn=isbn)
    book.views += 1
    await book.save()

    publisher = await book.publisher
    category = await book.category

    related_books = await Book.filter(category=category).limit(4)
    comments_query = Comment.filter(book=book)
    if (not user) or (user and not user.admin):
        comments_query = comments_query.filter(banned=False)

    comments = list(await comments_query)

    commenters_names = []
    for comment in comments:
        commenter = await comment.commenter
        commenters_names.append(commenter.name + " " + commenter.surname)

    book_sources = await DownloadSource.filter(book=book)

    return templates.TemplateResponse(
        "book-detail.html",
        {
            "request": request,
            "user": user,
            "book": book,
            "book_category": category.name,
            "book_publisher_name": publisher.name,
            "book_publisher_id": publisher.id,
            "book_sources": book_sources,
            "related_books": related_books,
            # Comments
            "comments": comments,
            "comments_count": len(comments),
            "commenters_names": commenters_names,
        }
        | notifications,
    )


@app.post("/book/{isbn}")
async def make_comment(
    request: Request,
    isbn: str,
    user: User = Depends(get_user),
    stars: int = Form(),
    message: str = Form(),
):
    if not user:
        raise ValueError("Anonyms cannot write comments")

    await Comment.create(
        commenter=user,
        book=await Book.get(isbn=isbn),
        stars=stars,
        message=message,
    )

    return RedirectResponse(request.url, status_code=status.HTTP_302_FOUND)


@app.post("/ban")
async def ban_comment(
    user: User = Depends(get_user),
    comment_id: str = Query(),
    isbn: str = Query(),
):
    if not user.admin:
        raise ValueError("Only admin can ban comments")

    comment = await Comment.get(id=comment_id)
    comment.banned = True
    await comment.save()

    return RedirectResponse(f"/book/{isbn}", status_code=status.HTTP_302_FOUND)


@app.post("/unban")
async def unban_comment(
    user: User = Depends(get_user),
    comment_id: str = Query(),
    isbn: str = Query(),
):
    if not user.admin:
        raise ValueError("Only admin can unban comments")

    comment = await Comment.get(id=comment_id)
    comment.banned = False
    await comment.save()

    return RedirectResponse(f"/book/{isbn}", status_code=status.HTTP_302_FOUND)


@app.get("/signin", response_class=HTMLResponse)
async def signin(request: Request):
    return templates.TemplateResponse(
        "signin.html",
        {
            "request": request,
            "nav_item": "SignIn",
        },
    )


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
    return templates.TemplateResponse(
        "signup.html",
        {
            "request": request,
            "nav_item": "SignUp",
        },
    )


@app.post("/signup")
async def signin(
    name: str = Form(),
    surname: str = Form(),
    email: str = Form(),
    password: str = Form(),
    bio: str = Form(),
):
    user = await User.create(
        admin=False,
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
    from random import randint, choice

    fake = Faker()

    categories = [
        (await Category.get_or_create(name="Classics"))[0],
        (await Category.get_or_create(name="Fantasy"))[0],
        (await Category.get_or_create(name="Poetry"))[0],
        (await Category.get_or_create(name="Biography"))[0],
        (await Category.get_or_create(name="Essays"))[0],
    ]

    sources = [
        {
            "filetype": "pdf",
            "url": "https://github.com/asdfjkl/neural_network_chess/releases/download/v1.5/Neural_Networks_For_Chess.pdf",
        },
        {
            "filetype": "epub",
            "url": "https://github.com/asdfjkl/neural_network_chess/releases/download/v1.5/Neural_Networks_For_Chess.pdf",
        },
    ]

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
            book = await Book.create(
                isbn=fake.isbn13(),
                author=author,
                title=fake.sentence(),
                description=fake.text(),
                category=choice(categories),
                image_url=f"https://placekitten.com/{randint(400, 600)}/{randint(600, 800)}",
                publisher=publisher,
                year=fake.year(),
                pages=randint(50, 1000),
                views=0,
            )

            for source in sources:
                await DownloadSource.create(
                    filetype=source["filetype"],
                    url=source["url"],
                    book=book,
                )

    return {"status": "Success"}


@app.post("/add_good_books")
async def add_good_books():
    from faker import Faker
    from random import randint, choice

    fake = Faker()

    category = await Category.create(name="Science")
    publisher = await Publisher.create(name="Alisher Publish")

    name, surname = fake.name().split(maxsplit=1)
    author = await Author.create(
        name=name,
        surname=surname,
        bio=fake.text(),
        email=fake.email(),
        password_hash="1234",
    )

    books_data = [
        {
            "title": "Algorithms Design Manual",
            "image_url": "/custom_books/algo_design_manual.jpg",
        },
        {
            "title": "C programming",
            "image_url": "/custom_books/c_programming.jpg",
        },
        {
            "title": "Fluent Python",
            "image_url": "/custom_books/fluent_python.jpg",
        },
        {
            "title": "Introduction to algorithms",
            "image_url": "/custom_books/introduction_to_alogorithms.jpg",
        },
        {
            "title": "Learning Go",
            "image_url": "/custom_books/learning_go.jpg",
        },
        {
            "title": "Microservices",
            "image_url": "/custom_books/microservices.jpg",
        },
        {
            "title": "Programming rust",
            "image_url": "/custom_books/programming_rust.jpg",
        },
        {
            "title": "Python distilled",
            "image_url": "/custom_books/python_distilled.jpg",
        },
        {
            "title": "Serverless systems",
            "image_url": "/custom_books/serverless_systems.jpg",
        },
        {
            "title": "System design Interview",
            "image_url": "/custom_books/system_design_interview.jpg",
        },
        {
            "title": "The Linux API",
            "image_url": "/custom_books/the_linux_api.jpg",
        },
    ]

    for data in books_data:
        book = await Book.create(
            isbn=fake.isbn13(),
            author=author,
            title=data["title"],
            description=fake.text(),
            category=category,
            image_url=data["image_url"],
            publisher=publisher,
            year=fake.year(),
            pages=randint(50, 1000),
            views=0,
        )

        await DownloadSource.create(
            book=book,
            filetype="pdf",
            url=(
                "https://github.com/"
                "asdfjkl/neural_network_chess/releases/download/v1.5/"
                "Neural_Networks_For_Chess.pdf"
            ),
        )


@app.get("/test")
async def test():
    query = Category.exists(name="111")
    return {"query": query.sql()}


app.mount(
    "/",
    StaticFiles(
        directory="static",
        html=True,
    ),
    name="static",
)
