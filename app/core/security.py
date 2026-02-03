from fastapi import HTTPException
from datetime import datetime, timedelta
import hashlib
from jose import jwt,JWTError,ExpiredSignatureError
import requests
from app.config.env import JWT_EXPIRE_DAYS,JWT_SECRET_KEY, JWT_ALGORITHM,JWT_EXPIRE_MINUTES,GOOGLE_CLIENT_ID

GOOGLE_CERTS_URL = "https://www.googleapis.com/oauth2/v3/certs"

def create_access_token(data: dict):
    to_encode = data.copy()
    to_encode["type"] = "access"
    expire = datetime.utcnow() + timedelta(minutes=JWT_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    return jwt.encode(
        to_encode,
        JWT_SECRET_KEY,
        algorithm=JWT_ALGORITHM
    )

def create_refresh_token(data:dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(days=float(JWT_EXPIRE_DAYS))
    to_encode["type"] = "refresh"
    to_encode.update({"exp":expire})
    token = jwt.encode(
        to_encode,
        JWT_SECRET_KEY,
        algorithm=JWT_ALGORITHM
    )
    return token,expire


def verify_token(token:str):
    try:
        payload = jwt.decode(
            token,
            algorithms=[JWT_ALGORITHM],
            key=JWT_SECRET_KEY
        )
        if payload.get("type")!="refresh":
            raise HTTPException(status_code=401,detail="Invalid token type")
        return payload
    except ExpiredSignatureError:
        raise HTTPException(status_code=401,detail='Expired Refresh token')
    except JWTError:
        raise HTTPException(status_code=401,detail="Invalid Refresh token")
    

def hash_token(token:str)->str:
    return hashlib.sha256(token.encode()).hexdigest()

def verify_google_token(token:str,client_id:str=GOOGLE_CLIENT_ID):
    certs = requests.get(GOOGLE_CERTS_URL).json()
    try:
        payload = jwt.decode(
            token,
            certs,
            algorithms=["RS256"],
            audience=client_id,
        )
        # if payload["iss"] not in ["accounts.google.com", "https://accounts.google.com"]: #security check for issuer
        #     raise HTTPException(status_code=401, detail="Invalid issuer")
        return payload
    except JWTError:
        return None