from db.db import engine
from db.base import Base
from fastapi import FastAPI, middleware
from fastapi.middleware.cors import CORSMiddleware
from routes import auth
from routes import upload
from routes import video

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(
    auth.router, prefix="/auth"
)  # connecting the router to the FastAPI()
app.include_router(upload.api_router, prefix="/upload/video")
app.include_router(video.api_router, prefix="/videos")


@app.get("/")
def root():
    return "Hello , World"


"""
This is binding all the model clases that extend Base and creating the tables in the DB
using the engine we defined in the db.py file
"""
Base.metadata.create_all(engine)
