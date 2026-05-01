from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import traceback

# ------------------ CREATE APP ------------------

app = FastAPI(
    title="NoteMind API",
    description="AI-Powered Knowledge & Memory Management System",
    version="1.0.0"
)

# ------------------ DATABASE ------------------

try:
    from database import Base, engine
    Base.metadata.create_all(bind=engine)
    print("✅ Database connected successfully")
except Exception as e:
    print("❌ DATABASE ERROR:")
    traceback.print_exc()

# ------------------ IMPORT ROUTES ------------------

try:
    from routes.notes import router as notes_router
    from routes.ai import router as ai_router
    from routes.upload import router as upload_router
    print("✅ Routes imported successfully")
except Exception as e:
    print("❌ ROUTE IMPORT ERROR:")
    traceback.print_exc()

# ------------------ CORS ------------------

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # later change to frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ------------------ INCLUDE ROUTERS ------------------

try:
    app.include_router(notes_router)
    app.include_router(ai_router)
    app.include_router(upload_router)
    print("✅ Routers attached")
except Exception as e:
    print("❌ ROUTER ATTACH ERROR:")
    traceback.print_exc()

# ------------------ ROOT ------------------

@app.get("/")
def root():
    return {
        "message": "NoteMind Backend Running Successfully 🚀"
    }
