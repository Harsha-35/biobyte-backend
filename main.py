from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import random

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class UserData(BaseModel):
    age: int
    weight: float
    height: float
    goal: str

@app.get("/")
def root():
    return {"message": "Biobyte Backend Running"}

@app.post("/generate-plan")
def generate_plan(user: UserData):
    bmr = 10*user.weight + 6.25*user.height - 5*user.age + 5

    if user.goal == "fat_loss":
        calories = bmr - 400
    elif user.goal == "muscle_gain":
        calories = bmr + 300
    else:
        calories = bmr

    protein = user.weight * 2
    smart_score = random.randint(75, 90)

    return {
        "calories": round(calories),
        "protein": round(protein),
        "smartScore": smart_score
    }