from fastapi import APIRouter


router = APIRouter(
    prefix='/api',
    tags=["authentication"],
    responses={404: {"description":"User not found"}},
)

@router.get("/me",summary="Authenticating me")
def auth():
    return "me"