from fastapi import FastAPI
from dotenv import load_dotenv
import os

load_dotenv()

app = FastAPI(title="Rapidread Summarizer API")

# Import routers (registered below)
from .routes import youtube, pdf, article, github

app.include_router(youtube.router, prefix="/youtube")
app.include_router(pdf.router, prefix="/pdf")
app.include_router(article.router, prefix="/article")
app.include_router(github.router, prefix="/github")


@app.get("/")
def root():
    return {"message": "Rapidread Summarizer API"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("backend.main:app", host="0.0.0.0", port=int(os.getenv("PORT", 8000)), reload=True)
