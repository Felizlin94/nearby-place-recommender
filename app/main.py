from fastapi import FastAPI
from app.api_routes import router as api_router

app = FastAPI()

app.include_router(api_router)


@app.get("/")
def root():
    return {"message": "Nearby Place Recommender is running"}
