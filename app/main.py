from fastapi import FastAPI

app = FastAPI(title="Claims Platform")

@app.get("/")
def root():
    return {"status": "running"}
    