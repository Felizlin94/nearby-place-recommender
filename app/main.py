from fastapi import FastAPI
from app import api_routes

app = FastAPI()

app.include_router(api_routes.router)


@app.get("/")
def root():
    return {"message": "Preference Place Recommender API is running!"}
