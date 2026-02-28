from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import requests
import os

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

GEMINI_API_KEY = ("AIzaSyCxL-KPLtgNd6R6Z6ij03nNY_uSA2GVTBA")

# ----------- MODELS -----------

class UserData(BaseModel):
    age: int
    weight: float
    height: float
    activity: str = "moderate"

class ChatMessage(BaseModel):
    message: str

class ProgressData(BaseModel):
    weight: float

class ImageData(BaseModel):
    image_base64: str

progress_data = []

# ----------- BMI + AI PLAN -----------

@app.post("/generate-plan")
def generate_plan(user: UserData):

    height_m = user.height / 100
    bmi = user.weight / (height_m ** 2)

    if bmi < 18.5:
        category = "Underweight"
        goal = "Weight Gain"
    elif bmi < 25:
        category = "Normal Weight"
        goal = "Maintain Weight"
    elif bmi < 30:
        category = "Overweight"
        goal = "Weight Loss"
    else:
        category = "Obese"
        goal = "Aggressive Fat Loss"

    # BMR (Mifflin-St Jeor male demo)
    bmr = 10 * user.weight + 6.25 * user.height - 5 * user.age + 5

    activity_map = {
        "sedentary": 1.2,
        "moderate": 1.55,
        "active": 1.75
    }

    tdee = bmr * activity_map.get(user.activity, 1.55)

    if goal == "Weight Loss":
        calories = int(tdee - 400)
    elif goal == "Weight Gain":
        calories = int(tdee + 300)
    else:
        calories = int(tdee)

    prompt = f"""
You are a certified nutrition expert.

User Details:
BMI: {round(bmi,2)}
Category: {category}
Goal: {goal}
Daily Calories: {calories}

Respond in structured format:

### BMI Analysis
### Diet Plan
### Workout Plan
### Tips
"""

    url = f"https://generativelanguage.googleapis.com/v1/models/gemini-2.5-flash:generateContent?key={GEMINI_API_KEY}"

    payload = {
        "contents": [{
            "parts": [{"text": prompt}]
        }]
    }

    response = requests.post(url, json=payload)

    if response.status_code != 200:
        return {"error": response.text}

    result = response.json()
    ai_text = result["candidates"][0]["content"]["parts"][0]["text"]

    return {
        "bmi": round(bmi, 2),
        "category": category,
        "goal": goal,
        "calories": calories,
        "aiPlan": ai_text
    }

# ----------- FOOD IMAGE ANALYSIS -----------

@app.post("/analyze-food")
def analyze_food(data: ImageData):

    prompt = """
Analyze the food in this image.
Provide:
- Food name
- Estimated calories
- Macronutrients
- Health rating
"""

    url = f"https://generativelanguage.googleapis.com/v1/models/gemini-2.5-flash:generateContent?key={GEMINI_API_KEY}"

    payload = {
        "contents": [{
            "parts": [
                {"text": prompt},
                {
                    "inlineData": {
                        "mimeType": "image/jpeg",
                        "data": data.image_base64
                    }
                }
            ]
        }]
    }

    response = requests.post(url, json=payload)

    if response.status_code != 200:
        return {"error": response.text}

    result = response.json()
    ai_text = result["candidates"][0]["content"]["parts"][0]["text"]

    return {"analysis": ai_text}

# ----------- CHAT -----------

@app.post("/chat")
def chat_ai(chat: ChatMessage):

    prompt = f"""
You are a professional nutrition coach.
User says: {chat.message}
Respond helpfully.
"""

    url = f"https://generativelanguage.googleapis.com/v1/models/gemini-2.5-flash:generateContent?key={GEMINI_API_KEY}"

    payload = {
        "contents": [{
            "parts": [{"text": prompt}]
        }]
    }

    response = requests.post(url, json=payload)

    result = response.json()
    reply = result["candidates"][0]["content"]["parts"][0]["text"]

    return {"reply": reply}

# ----------- PROGRESS TRACKING -----------

@app.post("/track-progress")
def track_progress(data: ProgressData):
    progress_data.append(data.weight)
    return {"data": progress_data}

@app.get("/progress")
def get_progress():
    return {"data": progress_data}