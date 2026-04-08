import os
import time
import logging
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

# --- Logging setup ---
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)
logger = logging.getLogger("booktracker")

app = FastAPI(title="BookTracker")
start_time = time.time()
requests_count = 0
books = {}
next_id = 1

logger.info("BookTracker starting | version=%s", os.getenv("APP_VERSION", "unknown"))


class BookCreate(BaseModel):
    title: str
    author: str


@app.middleware("http")
async def count_requests(request, call_next):
    global requests_count
    requests_count += 1
    response = await call_next(request)
    return response


# --- Routes ---
@app.get("/")
def root():
    return {"service": "booktracker", "status": "running"}


@app.get("/health")
def health():
    logger.debug("Health check called")
    return {"status": "healthy", "version": "v2"}


@app.get("/ready")
def ready():
    logger.debug("Readiness check called")
    return {"status": "ready"}


@app.get("/version")
def version():
    import socket
    return {
        "version": os.getenv("APP_VERSION", "unknown"),
        "hostname": socket.gethostname()
    }


@app.get("/books")
def list_books():
    return list(books.values())


@app.post("/books", status_code=201)
def create_book(book: BookCreate):
    global next_id
    new_book = {"id": next_id, "title": book.title, "author": book.author}
    books[next_id] = new_book
    logger.info("Book created | id=%d title='%s' author='%s'", next_id, book.title, book.author)
    next_id += 1
    return new_book


@app.get("/books/{book_id}")
def get_book(book_id: int):
    if book_id not in books:
        raise HTTPException(status_code=404, detail="Book not found")
    return books[book_id]


@app.delete("/books/{book_id}", status_code=204)
def delete_book(book_id: int):
    if book_id not in books:
        logger.warning("Delete failed | book_id=%d not found", book_id)
        raise HTTPException(status_code=404, detail="Book not found")
    logger.info("Book deleted | id=%d", book_id)
    del books[book_id]


@app.get("/metrics")
def metrics():
    return {
        "total_requests": requests_count,
        "uptime_seconds": round(time.time() - start_time, 2)
    }

