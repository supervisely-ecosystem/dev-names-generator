import os
import sys
from pathlib import Path
import signal

from fastapi import FastAPI, Request, WebSocket, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi_utils.timing import add_timing_middleware, record_timing
import jinja2
import psutil


# log app root directory
app_dir = str(Path(sys.argv[0]).parents[5])
print(f"App root directory: {app_dir}")
# sys.path.append(app_dir)

app: FastAPI = FastAPI()
add_timing_middleware(app, prefix="app")
ws: WebSocket = None
server_stopped = False


templates_dir = "templates"
templates = Jinja2Templates(directory=templates_dir)
templates.env = jinja2.Environment(
    loader=jinja2.FileSystemLoader(templates_dir),
    variable_start_string='{{{',
    variable_end_string='}}}',
)


@app.websocket("/ws")
async def init_websocket(websocket: WebSocket):
    global ws
    await websocket.accept()
    ws = websocket
    while True:
        data = await websocket.receive_json()


def shutdown_app():
    global server_stopped 
    server_stopped = True
    # https://github.com/tiangolo/fastapi/issues/1509
    current_process = psutil.Process(os.getpid())
    current_process.send_signal(signal.SIGINT) # emit ctrl + c


@app.middleware("http")
async def check_server_stopped(request: Request, call_next):
    if server_stopped:
      raise HTTPException(status_code=403, detail="Server is being shut down")
    response = await call_next(request)    
    return response


@app.post("/shutdown")
async def shutdown(request: Request):
    print("do something here")
    shutdown_app()