from fastapi import FastAPI
from app.database import engine, Base
from app.routers import auth, cases
from app.models import user, case, case_history

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Claims Platform")

app.include_router(auth.router)
app.include_router(cases.router)

@app.get("/")
def root():
    return {"status": "running"}