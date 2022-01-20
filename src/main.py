from fastapi import FastAPI, Request, WebSocket, HTTPException
from fastapi.templating import Jinja2Templates
from src.boilerplate import app, ws, templates, shutdown_app
import supervisely as sly

import names


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


@app.on_event("startup")
async def startup_event():
    print("init something before server starts")


@app.on_event("shutdown")
def shutdown_event():
    print("save something before shut down")