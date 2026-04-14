from fastapi import FastAPI
from app.database import engine, Base
from app.routers import auth, cases, comments, analytics
from app.models import user, case, case_history, comment

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Claims Platform")

app.include_router(auth.router)
app.include_router(cases.router)
app.include_router(comments.router)
app.include_router(analytics.router)

@app.get("/")
def root():
    return {"status": "running"}
    