import asyncio
import os
import sys
from pathlib import Path
from typing import Optional

from fastapi import FastAPI, Request, Depends
from fastapi.responses import JSONResponse

import supervisely as sly

from supervisely.fastapi_helpers import ShutdownMiddleware, shutdown, \
                                        WebsocketMiddleware, WebsocketManager, \
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



app = FastAPI()


# from fastapi.middleware.httpsredirect import HTTPSRedirectMiddleware
# from fastapi.middleware.trustedhost import TrustedHostMiddleware
# from fastapi.middleware.gzip import GZipMiddleware
# from starlette.middleware.base import BaseHTTPMiddleware
# app.add_middleware(BaseHTTPMiddleware, dispatch=func)

app.add_middleware(WebsocketMiddleware)
app.add_middleware(ShutdownMiddleware) 
app.add_middleware(StateMiddleware)
app.add_middleware(DataMiddleware)
# remove classmethods??? and reimplement to instance methods?

templates = Jinja2Templates(directory="templates")

#@TODO: try catch exceptions in async-await
#@TODO: initialize state / data on server (jsonpatch.JsonPatchConflict: can't replace a non-existent object 'counter')


@app.get("/")
async def read_index(request: Request):
    return templates.TemplateResponse('index.html', {'request': request})


@app.post("/sync-generate")
def sync_generate(request: Request):
    # example how to execute ASYNC methods in SYNC function
    json_body = async_to_sync(request.json)()
    time.sleep(1.5)
    # state["name"] = names.get_first_name()
    # async_to_sync(state.synchronize_changes())


@app.post("/generate")
async def generate(request: Request, state: StateJson = Depends(StateJson.from_request)):
    state["name"] = names.get_first_name()
    return state.get_changes()


@app.post("/generate-ws")
async def generate_ws(request: Request, state: StateJson = Depends(StateJson.from_request)):
    state["name"] = names.get_first_name()
    await state.synchronize_changes()
    # or
    # await WebsocketManager().broadcast(state.get_changes())


@app.post("/do-then-shutdown")
async def do_then_shutdown(request: Request, state: StateJson = Depends(StateJson.from_request)):
    print("do something here and then manual shutdown")
    shutdown(app)
    # or 
    # shutdown(request.app)


@app.post("/count")
async def count(request: Request, state: StateJson = Depends(StateJson.from_request)):
    for i in range(10):
        asyncio.sleep(1)
        state["counter"] = i
        await state.synchronize_changes()


@app.on_event("startup")
def startup_event():
    print("startup_event --- init something before server starts")


@app.on_event("shutdown")
def shutdown_event():
    print("shutdown_event --- do something before server shutdowns")
