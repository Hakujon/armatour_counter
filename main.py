from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from app.router import workpiece_router

app = FastAPI(title="Расчёт раскроя арматуры")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(workpiece_router)

app.mount("/", StaticFiles(directory="app/static", html=True), name="static")
