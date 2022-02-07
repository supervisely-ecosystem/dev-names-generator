import os
import sys
import asyncio
import time
import json
from dotenv import load_dotenv
from asgiref.sync import async_to_sync
from fastapi import FastAPI, Request, Depends
import supervisely as sly
import names


app_dir = os.getcwd()  # app root directory (working directory)
sys.path.append(app_dir)
print(f"App root directory: {app_dir}")


# load env variables from file for debug (has no effect in production)
load_dotenv(os.path.join(app_dir, "debug.env"))


# init state and data (singletons)
sly.app.LastStateJson({ "name": "abc", "counter": 0})
sly.app.DataJson({"max": 123, "counter": 0})


app = FastAPI()
sly_app = sly.app.fastapi.create()
app.mount("/sly", sly_app)
templates = sly.app.fastapi.Jinja2Templates(directory="templates")


@app.get("/")
async def read_index(request: Request):
    return templates.TemplateResponse('index.html', {'request': request})


@app.post("/generate")
async def generate(request: Request, state: sly.app.StateJson = Depends(sly.app.StateJson.from_request)):
    state["name"] = names.get_first_name()
    await state.synchronize_changes()
    #return state.get_changes()  # hidden functionality
    
    # for debug to test app data directory real-time synchroniation with team files
    file_path = os.path.join(sly.app.get_data_dir(), "data.json")
    with open(file_path, 'w') as my_demo_file:
        json.dump(state, my_demo_file, indent=4)


@app.post("/generate-ws")
async def generate_ws(request: Request, state: sly.app.StateJson = Depends(sly.app.StateJson.from_request)):
    state["name"] = names.get_first_name()
    await state.synchronize_changes()  # use websocket to send state changes to client


@app.post("/sync-generate")
def sync_generate(request: Request, state: sly.app.StateJson = Depends(sly.app.StateJson.from_request)):
    state["name"] = names.get_first_name()
    time.sleep(50)
    async_to_sync(state.synchronize_changes)()


@app.post("/do-then-shutdown")
async def do_then_shutdown(request: Request, state: sly.app.StateJson = Depends(sly.app.StateJson.from_request)):
    print("do something here and then manual shutdown")
    sly.app.fastapi.shutdown()


@app.post("/count-state")
async def count_state(request: Request, state: sly.app.StateJson = Depends(sly.app.StateJson.from_request)):
    for i in range(10):
        await asyncio.sleep(0.5)
        state["counter"] = i
        await state.synchronize_changes()


@app.post("/count-data")
async def count_state(request: Request, state: sly.app.StateJson = Depends(sly.app.StateJson.from_request)):
    data = sly.app.DataJson() # singleton
    for i in range(10):
        await asyncio.sleep(0.5)
        data["counter"] = i
        await data.synchronize_changes()


@app.on_event("startup")
def startup_event():
    print("startup_event --- init something before server starts")
    sly.app.get_data_dir()
    


@app.on_event("shutdown")
def shutdown_event():
    print("shutdown_event --- do something before server shutdowns")
