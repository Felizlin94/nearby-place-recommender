from fastapi import APIRouter

router = APIRouter()


@router.get("/recommend")
def recommend():
    return {"message": "Here is your recommendation"}


@router.get("/places")
def get_places():
    return {"message": "Nearby places"}
