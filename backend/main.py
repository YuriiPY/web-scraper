from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import uvicorn
import os
from sqlalchemy.orm import Session

from storage.database import init_db
from scraper_engine.polskie_radio import gather_news

app = FastAPI()

os.makedirs("pdfs", exist_ok=True)
app.mount("/pdfs", StaticFiles(directory="pdfs"), name="pdfs")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://localhost:3000",
        "http://localhost:3001",
        "http://localhost:8081",
        "http://localhost:8001",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/article")
def get_article(word: str, start_date: str, end_date: str):
    articles = gather_news(word, start_date, end_date)

    return articles


if __name__ == "__main__":
    init_db()
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
