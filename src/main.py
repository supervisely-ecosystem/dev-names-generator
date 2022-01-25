import os
import sys
from pathlib import Path

from fastapi import FastAPI, Request, WebSocket
import supervisely as sly
from supervisely.fastapi_helpers import WebsocketManager, ShutdownMiddleware

from supervisely.fastapi_helpers import Jinja2Templates

# from fastapi.middleware.httpsredirect import HTTPSRedirectMiddleware
# from fastapi.middleware.trustedhost import TrustedHostMiddleware

import names
import time
from asgiref.sync import async_to_sync


# https://stackoverflow.com/questions/1229068/with-python-can-i-keep-a-persistent-dictionary-and-modify-it
# https://stackoverflow.com/questions/53882241/detect-changes-to-a-nested-dictionary-with-python/53882459
# https://treyhunner.com/2019/04/why-you-shouldnt-inherit-from-list-and-dict-in-python/
# https://github.com/seperman/deepdiff
# https://github.com/xlwings/jsondiff
# https://github.com/stefankoegl/python-json-patch

state = {}
data = {}

# log app root directory
app_dir = str(Path(sys.argv[0]).parents[5])
print(f"App root directory: {app_dir}")
sys.path.append(app_dir)


app: FastAPI = FastAPI()
app.add_middleware(ShutdownMiddleware)
templates = Jinja2Templates(directory="templates")
ws_manager = WebsocketManager()

# state - from client (always replace)
# data - server

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
    state = await request.json()
    await ws_manager.broadcast({'name': names.get_first_name()})


@app.on_event("startup")
def startup_event():
    print("init something before server starts")


@app.on_event("shutdown")
def shutdown_event():
    print("do something before server shutdowns")


@app.websocket("/sly-ws")
async def websocket_endpoint(websocket: WebSocket):
    await ws_manager.endpoint(websocket)