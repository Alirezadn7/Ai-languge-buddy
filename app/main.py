from fastapi import FastAPI, status

from app.config import settings

app = FastAPI(
    title=settings.APP_NAME,
    debug=settings.DEBUG_MODE,
)

@app.get("/" , status_code=status.HTTP_200_OK , tags=["General"])
async def root():
    return {
        "app_name":settings.APP_NAME,
        "debug_mode":settings.DEBUG_MODE,
        "message": "AI Language Buddy API is running!",
    }

@app.get("/health", status_code=status.HTTP_200_OK, tags=["General"])
async def health_check():
    return {
        "status": "healthy",
    }