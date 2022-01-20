import os
import sys
from pathlib import Path

from fastapi import FastAPI, Request, WebSocket
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import jinja2

# import supervisely as sly
import names

import time
import psutil
import threading

# log app root directory
app_dir = str(Path(sys.argv[0]).parents[5])
print(f"App root directory: {app_dir}")
# sys.path.append(app_dir)


app = FastAPI()
ws: WebSocket = None


templates_dir = "templates"
templates = Jinja2Templates(directory=templates_dir)
templates.env = jinja2.Environment(
    loader=jinja2.FileSystemLoader(templates_dir),
    variable_start_string='{{{',
    variable_end_string='}}}',
)


@app.get("/")
async def read_index(request: Request):
    return templates.TemplateResponse('index.html', {'request': request})


@app.post("/generate")
async def generate(request: Request):
    state = await request.json()
    state["name"] = names.get_first_name()
    return state


@app.post("/generate-ws")
async def generate_ws(request: Request):
    await ws.send_json({'name': names.get_first_name()})



@app.post("/stop")
async def stop(request: Request):
    import signal
    print("do something here")
    # https://github.com/tiangolo/fastapi/issues/1509
    parent = psutil.Process(psutil.Process(os.getpid()).ppid())
    parent.send_signal(signal.SIGINT) # KeyboardInterrupt
    

@app.websocket("/ws")
async def init_websocket(websocket: WebSocket):
    global ws
    await websocket.accept()
    ws = websocket
    while True:
        data = await websocket.receive_json()
