from fastapi import FastAPI
from api.routes.image_routes import router as image_router
from api.routes.video_routes import router as video_router

app = FastAPI()

app.include_router(image_router, prefix="/image")
app.include_router(video_router, prefix="/video")
