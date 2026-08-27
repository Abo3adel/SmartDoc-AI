from fastapi import FastAPI
from api.routes import router 

app = FastAPI(title="LLM Task API")

app.include_router(router)

@app.get("/")
async def root():
    return {"message": "Welcome to our structured LLM API!"}