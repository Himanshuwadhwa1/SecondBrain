from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

import os
from app.routers.auth import router as auth
from app.config.db import lifespan

if os.getenv("DEBUG", "false").lower() == "true":
    import debugpy
    if not debugpy.is_client_connected():
        debugpy.listen(("0.0.0.0",5678))
        print("wait for debugger...")



app = FastAPI(lifespan=lifespan)

app.title = "The maag server"

app.add_middleware(
    CORSMiddleware,
    allow_origins = ["*"],
    allow_credentials = True,
    allow_methods = ["*"],
    allow_headers = ["*"],
    )

app.include_router(auth)