from fastapi import FastAPI, Request, WebSocket, HTTPException, WebSocketDisconnect
from fastapi.templating import Jinja2Templates
from src.boilerplate import app, templates
import supervisely as sly
from supervisely.fastapi import WebsocketManager, ShutdownMiddleware 


import names
import time
from asgiref.sync import async_to_sync

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
