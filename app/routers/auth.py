from fastapi import APIRouter,Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.config.db import get_db
from app.models.user import User
from app.core.security import verify_google_token, create_access_token

router = APIRouter(
    prefix='/auth',
    tags=["authentication"],
    responses={404: {"description":"User not found"}},
)

@router.get("/me",summary="Authenticating me")
def auth():
    return "me"

@router.post('/google',summary="Logging in by google")
async def google_login(data:dict,db:AsyncSession = Depends(get_db)):
    id_token = data.get("id_token")
    if not id_token:
        raise HTTPException(status_code=400,detail="ID Token missing")
    payload = verify_google_token(id_token)
    if not payload:
        raise HTTPException(status_code=401,detail="Invalide id token")
    if payload["iss"] not in ["accounts.google.com", "https://accounts.google.com"]: #security check for issuer
        raise HTTPException(status_code=401, detail="Invalid issuer")
    if not payload.get("email_verified"):
        raise HTTPException(status_code=401,detail="Email not verified by Google")
    
    google_id = payload["sub"]
    email = payload["email"]
    name = payload.get("name")
    picture = payload.get("picture")

    result = await db.execute(select(User).where(User.google_id == google_id))
    user = result.scalar_one_or_none()
    if not user:
        user = User(
            email = email,
            name = name,
            google_id = google_id,
            avatar_url = picture
        )
        try:
            db.add(user)
            await db.commit()
            await db.refresh(user)
        except Exception:
            await db.rollback()
            raise
    access_token  = create_access_token({"user_id":str(user.id)})
    response = {
        "access_token":access_token,
        "token_type":"bearer",
        "user":{
            "id": str(user.id),
            "email": user.email,
            "name": user.name
        }
    }


    return response