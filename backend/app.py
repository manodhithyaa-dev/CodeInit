from fastapi import FastAPI
from database import engine
from models import user_model
from routes import auth_routes

app = FastAPI()

# Create tables
user_model.Base.metadata.create_all(bind=engine)

app.include_router(auth_routes.router)

@app.get("/")
def root():
    return {"message": "Backend Running 🔥"}