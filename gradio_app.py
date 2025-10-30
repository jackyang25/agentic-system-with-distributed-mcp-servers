import gradio as gr
import uvicorn
from fastapi import FastAPI

from web_server.gr_interface import create_interface
from web_server.server import app

analysis_context = None
demo: gr.Blocks = create_interface()
app: FastAPI = gr.mount_gradio_app(app=app, blocks=demo, path="/")

if __name__ == "__main__":
    uvicorn.run(app=app, host="0.0.0.0", port=8000)
