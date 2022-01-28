import os
import sys
from pathlib import Path
from typing import Optional

from fastapi import FastAPI, Request, Depends
from fastapi.responses import JSONResponse

import supervisely as sly

from supervisely.fastapi_helpers import ShutdownMiddleware, shutdown, \
                                        WebsocketMiddleware, \
                                        StateMiddleware, \
                                        DataMiddleware
from supervisely.fastapi_helpers import Jinja2Templates
from supervisely.fastapi_helpers import StateJson, DataJson, LastStateJson, ContextJson

import names
import time
from asgiref.sync import async_to_sync

# # log app root directory
# app_dir = str(Path(sys.argv[0]).parents[5])
# print(f"App root directory: {app_dir}")
# sys.path.append(app_dir)

from fastapi.middleware.httpsredirect import HTTPSRedirectMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.middleware.gzip import GZipMiddleware

app = FastAPI()

from starlette.middleware.base import BaseHTTPMiddleware
# app.add_middleware(BaseHTTPMiddleware, dispatch=func)

# app.add_middleware(WebsocketMiddleware) # sub app #@TODO - reimplement?????
app.add_middleware(ShutdownMiddleware) 
app.add_middleware(StateMiddleware)     # sub app #@TODO - reimplement
# app.add_middleware(DataMiddleware)      # sub app #@TODO - reimplement to route???
# remove classmethods??? and reimplement to instance methods?

templates = Jinja2Templates(directory="templates")

#@TODO: middleware broken request 
# can not use multiple times
# request = Request(scope, receive, send)
#@TODO: statejson as depends

@app.get("/")
async def read_index(request: Request):
    return templates.TemplateResponse('index.html', {'request': request})

# @app.middleware("http")
# async def add_process_time_header(request: Request, call_next):
#     start_time = time.time()
#     response = await call_next(request)
#     process_time = time.time() - start_time
#     response.headers["X-Process-Time"] = str(process_time)
#     return response

# @app.post("/sync-generate")
# def sync_generate(request: Request):
#     # example how to execute ASYNC methods in SYNC function
#     state = async_to_sync(request.json)()
#     time.sleep(5)
#     state["name"] = names.get_first_name()
#     async_to_sync(state.synchronize_changes())


@app.post("/generate")
async def generate(request: Request):
    state = await request.json()
    #state = await StateJson.from_request(request)
    x = 10
    x += 1
    # state["name"] = names.get_first_name()
    # state.synchronize_changes()


@app.post("/generate-ws")
async def generate_ws(request: Request):
    pass
    # state = await request.json()
    # await ws_manager.broadcast({'name': names.get_first_name()})


@app.on_event("startup")
def startup_event():
    print("init something before server starts")


@app.on_event("shutdown")
def shutdown_event():
    print("do something before server shutdowns")
