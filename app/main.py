from fastapi import FastAPI,Request,HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

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

@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "success": False,
            "error": exc.detail,
        },
    )

@app.api_route("/{path:path}",methods=["GET","POST","PUT","PATCH","DELETE","OPTIONS","HEAD"])
async def catch_all(path:str,request:Request):
    return {
        "method": request.method,
        "path": path,
        "found": False
    }