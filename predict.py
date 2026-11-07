import joblib
import pandas as pd
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware  # 1. Import CORSMiddleware
from pydantic import BaseModel

# 1. Load the trained model artifact
model = joblib.load('model.bin')

# 2. Define the input schema using Pydantic
class ParkRequest(BaseModel):
    park_name: str
    month: int
    dow_number: int
    is_weekend: int
    operating_minutes: float
    has_early_entry: int
    has_extended_evening: int
    has_special_event: int
    is_holiday: int
    is_rainy: int

app = FastAPI(title="MagicQueue Crowd Predictor", description="API for predicting Disney park crowd levels.")

# 3. Add CORS Middleware right here (Allows your Netlify static frontend to talk to this API)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins (change to your specific Netlify URL later for extra security if desired)
    allow_credentials=True,
    allow_methods=["*"],  # Allows all HTTP methods (GET, POST, etc.)
    allow_headers=["*"],  # Allows all headers
)

@app.post("/predict")
def predict(payload: ParkRequest):
    # Convert incoming JSON payload to a DataFrame
    input_data = pd.DataFrame([payload.dict()])
    
    # Recreate the exact one-hot encoding used during training 
    all_parks = ['Magic Kingdom', 'Disney\'s Hollywood Studios', 'Disney\'s Animal Kingdom', 'Universal Studios Florida']
    
    # One-hot encode park_name manually or via get_dummies matching training
    input_encoded = pd.get_dummies(input_data, columns=['park_name'], drop_first=True)
    
    # Ensure all training columns match what the model expects
    expected_columns = model.feature_names_in_
    for col in expected_columns:
        if col not in input_encoded.columns:
            input_encoded[col] = 0
            
    # Reorder columns to match model expectation exactly
    input_encoded = input_encoded[expected_columns]

    # Make prediction
    prediction = model.predict(input_encoded)[0]

    return {
        "predicted_crowd_level_pct": round(float(prediction), 2),
        "status": "success"
    }

@app.get("/")
def home():
    return {"message": "Welcome to the MagicQueue API! Send a POST request to /predict."}