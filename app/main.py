from fastapi import FastAPI
from app.database import engine, Base
from app.routers import auth

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Claims Platform")

app.include_router(auth.router)

@app.get("/")
def root():
    return {"status": "running"}