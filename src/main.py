import os
import sys
from pathlib import Path

from fastapi import FastAPI, Request, WebSocket
from fastapi.responses import JSONResponse

import supervisely as sly
from supervisely.fastapi_helpers import \
    WebsocketManager, Jinja2Templates, \
    ShutdownMiddleware, StateMiddleware, DataMiddleware

import names
import time
from asgiref.sync import async_to_sync


# # log app root directory
# app_dir = str(Path(sys.argv[0]).parents[5])
# print(f"App root directory: {app_dir}")
# sys.path.append(app_dir)


app: FastAPI = FastAPI()

# ws_manager = WebsocketManager()
templates = Jinja2Templates(directory="templates")

app.add_middleware(ShutdownMiddleware)
app.add_middleware(StateMiddleware) #, state=state) # создаем sly_app_ws и методы
app.add_middleware(DataMiddleware) #, data=data) # создаем sly_app_ws и методы
# app.add_api_websocket_route(path=ws_manager.path, endpoint=ws_manager.endpoint)



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
    # request.app.data["5"] = 213
    # or app.data["5"] = 213
    # app.update_data()

    state = await request.json()
    state["name"] = names.get_first_name()
    return state


@app.post("/generate-ws")
async def generate_ws(request: Request):
    pass
    # state = await request.json()
    # await ws_manager.broadcast({'name': names.get_first_name()})


@app.post("/sly-app-state")
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
