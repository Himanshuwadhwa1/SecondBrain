from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from os import environ

from app.routers import auth
from app.config.db import lifespan

if environ.get('DEBUG'):
    import debugpy
    debugpy.listen(5678)
    debugpy.wait_for_client()



app = FastAPI(lifespan=lifespan)

app.title = "The maag server"

app.add_middleware(
    CORSMiddleware,
    allow_origins = ["*"],
    allow_credentials = True,
    allow_methods = ["*"],
    allow_headers = ["*"],
    )

app.include_router(auth.router)