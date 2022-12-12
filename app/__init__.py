from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from tortoise.contrib.fastapi import register_tortoise
from app.models import User

################### Settings
APP_URL = "postgres://demo:demo@localhost:5432/superlib"

app = FastAPI(
    title="SuperLib",
    description="Websystem for sharing both physical and electronic books",
    version="0.1.0",
)
app.mount("/", StaticFiles(directory="templates"), name="templates")
register_tortoise(
    app,
    db_url=APP_URL,
    modules={"models": ["app.models"]},
    generate_schemas=True,
)


################### Routers
@app.post("/register")
async def register():
    user = await User.create(
        name="Alisher",
        surname="Zhubanyshev",
        email="zhubanysh.alisher@gmail.com",
        password_hash="1234",
    )
    return {"message": user.name}


@app.post("/signin")
async def signin():
    return {"message": "WIP"}
