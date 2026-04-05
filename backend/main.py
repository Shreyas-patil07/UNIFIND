from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from config import settings
from database import init_firebase
from routes import products, users, chats, reviews, need_board

app = FastAPI(
    title="UNIFIND API",
    description="College marketplace platform API",
    version="2.0.0"
)

# CORS Configuration
origins = settings.CORS_ORIGINS.split(",")
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize Firebase on startup
@app.on_event("startup")
async def startup_event():
    init_firebase()

# Include routers
app.include_router(products.router, prefix="/api", tags=["products"])
app.include_router(users.router, prefix="/api", tags=["users"])
app.include_router(chats.router, prefix="/api", tags=["chats"])
app.include_router(reviews.router, prefix="/api", tags=["reviews"])
app.include_router(need_board.router, prefix="/api", tags=["need-board"])

@app.get("/")
async def root():
    return {"message": "UNIFIND API v2.0.0", "status": "running"}

@app.get("/api/health")
async def health_check():
    return {"status": "healthy", "version": "2.0.0"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
