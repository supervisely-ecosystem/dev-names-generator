import os
import sys
from pathlib import Path
from typing import Optional

from fastapi import FastAPI, Request, WebSocket, Depends
from fastapi.responses import JSONResponse

import supervisely as sly

from supervisely.fastapi_helpers import ShutdownMiddleware, shutdown
from supervisely.fastapi_helpers import WebsocketManager, Jinja2Templates

import names
import time
from asgiref.sync import async_to_sync

# from fastapi.middleware.trustedhost import TrustedHostMiddleware
# from fastapi.middleware.gzip import GZipMiddleware

# # log app root directory
# app_dir = str(Path(sys.argv[0]).parents[5])
# print(f"App root directory: {app_dir}")
# sys.path.append(app_dir)

app: FastAPI = FastAPI()

ws_manager = WebsocketManager()
templates = Jinja2Templates(directory="templates")

app.add_middleware(ShutdownMiddleware)
# app.add_middleware(StateMiddleware)
# app.add_middleware(DataMiddleware) #, data=data) # создаем sly_app_ws и методы
app.add_api_websocket_route(path=ws_manager.path, endpoint=ws_manager.endpoint)


async def add_process_time_header(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = str(process_time)
    return response


# lock state and data
# https://pymotw.com/3/asyncio/synchronization.html


subapi = FastAPI()
@subapi.get("/abc")
def read_sub():
    return {"message": "Hello World from sub API"}
app.mount("/subapi", subapi)


@app.get("/")
async def read_index(request: Request):
    return templates.TemplateResponse('index.html', {'request': request})


@app.post("/sync-generate")
def sync_generate(request: Request):
    state = async_to_sync(request.json)()
    time.sleep(5)
    state["name"] = names.get_first_name()
    return state


@app.post("/generate")
async def generate(request: Request):
    state = await request.json()
    state["name"] = names.get_first_name()
    return state


@app.post("/generate-ws")
async def generate_ws(request: Request):
    pass
    # state = await request.json()
    # await ws_manager.broadcast({'name': names.get_first_name()})


# @app.post("/abccs")
# async def do_then_shutdown(request: Request):
#     print("do something")
#     app.shutdown()


@app.on_event("startup")
def startup_event():
    print("init something before server starts")


@app.on_event("shutdown")
def shutdown_event():
    print("do something before server shutdowns")
