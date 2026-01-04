from fastapi import HTTPException
from datetime import datetime, timedelta
from jose import jwt,JWTError
import requests
from app.config.env import JWT_EXPIRE_DAYS,JWT_SECRET_KEY, JWT_ALGORITHM

GOOGLE_CERTS_URL = "https://www.googleapis.com/oauth2/v3/certs"

def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(days=JWT_EXPIRE_DAYS)
    to_encode.update({"exp": expire})
    return jwt.encode(
        to_encode,
        JWT_SECRET_KEY,
        algorithm=JWT_ALGORITHM
    )

def verify_google_token(token:str,client_id:str):
    certs = requests.get(GOOGLE_CERTS_URL).json()
    try:
        payload = jwt.decode(
            token,
            certs,
            algorithms=[JWT_ALGORITHM],
            audience=client_id
        )
        # if payload["iss"] not in ["accounts.google.com", "https://accounts.google.com"]: #security check for issuer
        #     raise HTTPException(status_code=401, detail="Invalid issuer")
        return payload
    except JWTError:
        return None