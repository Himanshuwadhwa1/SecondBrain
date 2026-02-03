from fastapi import APIRouter,Depends, HTTPException, Response, Request
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select,delete
from datetime import datetime,timezone

from app.config.db import get_db
from app.models.Table import User,Refresh_Token
from app.core.security import verify_google_token, create_access_token, create_refresh_token, hash_token,verify_token

router = APIRouter(
    prefix='/auth',
    tags=["authentication"],
    responses={404: {"description":"User not found"}},
)

@router.get("/me",summary="Authenticating me")
def auth():
    return "me"

@router.post('/google',summary="Logging in by google")
async def google_login(data:dict,response:Response,db:AsyncSession = Depends(get_db)):
    id_token = data.get("id_token")
    if not id_token:
        raise HTTPException(status_code=400,detail="ID Token missing")
    payload = verify_google_token(id_token)
    if not payload:
        raise HTTPException(status_code=401,detail="Invalid id token")
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
        except Exception as e:
            print(f"Error occured while inserting: {e} ")
            await db.rollback()
            raise
    access_token  = create_access_token({"user_id":str(user.id)})
    refresh_token,expires_at  = create_refresh_token({"user_id":str(user.id)})
    hashed_refresh_token = hash_token(refresh_token)
    if refresh_token:
        token = Refresh_Token(
            user_id = user.id,
            jti = hashed_refresh_token,
            expires_at=expires_at
        )
        delete_old_token = delete(Refresh_Token).where(Refresh_Token.user_id==user.id)
        try:
            await db.execute(delete_old_token)
            db.add(token)
            await db.commit()
            await db.refresh(token)
        except Exception as e:
            print(f"Error occured while inserting: {e} ")
            await db.rollback()
            raise

    response.set_cookie(
        key="refresh_token",
        value=refresh_token,
        httponly=True,
        secure=True,
        samesite="strict",
        path="/auth/refresh"
        )
    return {
        "access_token":access_token,
        "token_type":"bearer",
        "user":{
            "id": str(user.id),
            "email": user.email,
            "name": user.name
        }
    }

@router.post('/refresh',summary="Getting new access token")
async def refreshing_token(request:Request,response:Response,db:AsyncSession=Depends(get_db)):
    refresh_token = request.cookies.get("refresh_token")
    payload = verify_token(refresh_token)

    if not payload:
        raise HTTPException(status_code=401,detail="Invalid Token")
    hashed_refresh_token = hash_token(refresh_token)
    stmt = select(Refresh_Token).where(Refresh_Token.jti == hashed_refresh_token)
    result = await db.execute(stmt)
    db_token = result.scalar_one_or_none()

    if not db_token:
        raise HTTPException(status_code=401,detail="No token found, login again")
    
    if db_token.expires_at < datetime.now(timezone.utc):
        raise HTTPException(status_code=401,detail="Token expired, Login Again")
    user_id = db_token.user_id
    access_token  = create_access_token({"user_id":str(user_id)})

    # in progress
    return {
        "access_token":access_token,
        "token_type":"bearer",
    }