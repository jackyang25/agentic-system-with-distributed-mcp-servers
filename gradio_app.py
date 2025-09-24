import gradio as gr
from fastapi import FastAPI

from web_server.gr_interface import create_interface
from web_server.server import app

# Mount the Gradio interface to FastAPI
analysis_context = None
demo: gr.Blocks = create_interface()
app: FastAPI = gr.mount_gradio_app(app=app, blocks=demo, path="/")

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app=app, host="0.0.0.0", port=8000)
