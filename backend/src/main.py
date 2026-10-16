import uvicorn
from fastapi import FastAPI
from src.api.v1.router import api_router
import src.core.models
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="RepCore", version="1.0.0")

app.include_router(api_router, prefix="/api/v1")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
    )
