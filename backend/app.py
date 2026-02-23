from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from database import engine
from models import user_model
from models import (
    journal_model,
    medication_model,
    medication_log_model,
    fitness_log_model,
    circle_model,
    circle_member_model,
    message_model
)
from routes import auth_routes
from routes import journal_routes
from routes import medication_routes
from routes import fitness_routes
from routes import circle_routes
from routes import insights_routes

app = FastAPI(
    title="MindMesh API",
    description="AI-Powered Behavioral Health & Habit Reinforcement Platform",
    version="1.0.0"
)

# CORS middleware - allow frontend to connect
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

user_model.Base.metadata.create_all(bind=engine)

app.include_router(auth_routes.router, prefix="/api")
app.include_router(journal_routes.router, prefix="/api")
app.include_router(medication_routes.router, prefix="/api")
app.include_router(fitness_routes.router, prefix="/api")
app.include_router(circle_routes.router, prefix="/api")
app.include_router(insights_routes.router, prefix="/api")

@app.get("/")
def root():
    return {"message": "MindMesh Backend Running"}

@app.get("/health")
def health_check():
    return {"status": "healthy"}
