from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from auth import router as auth_router
from leave import router as leave_router
from utils import initialize_storage

import os

app = FastAPI(
    title="LeaveTrack Backend",
    version="1.0.0"
)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

UPLOAD_DIR = os.path.join(BASE_DIR, "uploads")

os.makedirs(UPLOAD_DIR, exist_ok=True)

app.mount(
    "/uploads",
    StaticFiles(directory=UPLOAD_DIR),
    name="uploads"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://127.0.0.1:5500",
        "http://localhost:5500",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(
    leave_router,
    prefix="/leave",
    tags=["Leave"],
)

app.include_router(
    auth_router,
    prefix="/auth",
    tags=["Authentication"],
)


@app.on_event("startup")
def startup():
    initialize_storage()
    print("Storage Initialized")


@app.get("/")
def home():
    return {
        "message": "LeaveTrack Backend Running"
    }