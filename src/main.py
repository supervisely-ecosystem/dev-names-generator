from fastapi import FastAPI, Request, WebSocket, HTTPException, WebSocketDisconnect
from fastapi.templating import Jinja2Templates
from src.boilerplate import app, templates
import supervisely as sly
from fastapi.middleware.httpsredirect import HTTPSRedirectMiddleware
# from fastapi.middleware.gzip import GZipMiddleware
# from unicorn import UnicornMiddleware
from supervisely.fastapi import WebsocketManager, ShutdownMiddleware

import names
import time
from asgiref.sync import async_to_sync

ws_manager = WebsocketManager()
app.add_middleware(ShutdownMiddleware, path='/shutdown')


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


@app.post("/shutdown")
async def shutdown(request: Request):
    # button illustrates how to shutdown app programmatically
    await graceful_shutdown(app)


@app.on_event("startup")
async def startup_event():
    print("init something before server starts")


@app.on_event("shutdown")
def shutdown_event():
    print("do something before server shutdowns")


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await ws_manager.endpoint(websocket)