import os
import sys
from pathlib import Path

from fastapi import FastAPI, Request
import supervisely as sly
from supervisely.fastapi_helpers import WebsocketManager, ShutdownMiddleware, Jinja2Templates 


import names
import time
from asgiref.sync import async_to_sync

# log app root directory
app_dir = str(Path(sys.argv[0]).parents[5])
print(f"App root directory: {app_dir}")
sys.path.append(app_dir)


app: FastAPI = FastAPI()
templates = Jinja2Templates(directory="templates")
ws_manager = WebsocketManager()
app.add_middleware(ShutdownMiddleware, path='/shutdown')
app.add_api_websocket_route(path='/ws', endpoint=ws_manager.endpoint)


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
async def startup_event():
    print("init something before server starts")


@app.on_event("shutdown")
def shutdown_event():
    print("do something before server shutdowns")
