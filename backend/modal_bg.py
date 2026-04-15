import modal

app = modal.App("bg-remove")

image = modal.Image.debian_slim().pip_install(
    "fastapi",
    "python-multipart",
    "rembg",
    "pillow",
    "onnxruntime",
)

@app.function(image=image)
@modal.asgi_app()
def fastapi_app():
    from fastapi import FastAPI, UploadFile, File
    from fastapi.responses import Response
    from rembg import remove

    web_app = FastAPI()

    @web_app.post("/remove-bg")
    async def remove_bg_api(file: UploadFile = File(...)):
        image_bytes = await file.read()
        output = remove(image_bytes)
        return Response(content=output, media_type="image/png")

    return web_app