import streamlit as st
import requests
import pandas as pd

# 1. Page Configuration & Styling
st.set_page_config(
    page_title="MagicQueue - Disney Crowd Predictor",
    page_icon="🏰",
    layout="centered"
)

st.title("🏰 MagicQueue: Disney Park Crowd Predictor")
st.markdown("""
Predict Walt Disney World park crowd level percentages to optimize your vacation planning.
""")

st.divider()

# 2. Input Form Elements
st.header("1. Select Visit Details")

col1, col2 = st.columns(2)

with col1:
    park_name = st.selectbox(
        "Theme Park",
        ["Epcot", "Magic Kingdom", "Disney's Hollywood Studios", "Disney's Animal Kingdom"]
    )
    month = st.slider("Month", min_value=1, max_value=12, value=7)
    dow_number = st.selectbox(
        "Day of Week",
        options=[0, 1, 2, 3, 4, 5, 6],
        format_func=lambda x: ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"][x]
    )
    is_weekend = 1 if dow_number in [5, 6] else 0

with col2:
    operating_minutes = st.number_input("Operating Minutes (e.g. 720 = 12 hrs)", min_value=240, max_value=1440, value=780, step=30)
    is_holiday = st.checkbox("Is it a Major Holiday?", value=False)
    is_rainy = st.checkbox("Is Rain Forecasted?", value=False)
    has_early_entry = st.checkbox("Early Theme Park Entry Available?", value=True)
    has_extended_evening = st.checkbox("Extended Evening Hours Available?", value=False)
    has_special_event = st.checkbox("Special Event Scheduled? (e.g. After Hours)", value=False)

st.divider()

# 3. Prediction API Request
if st.button("🔮 Predict Crowd Level", use_container_width=True, type="primary"):
    payload = {
        "park_name": park_name,
        "month": month,
        "dow_number": dow_number,
        "is_weekend": is_weekend,
        "operating_minutes": float(operating_minutes),
        "has_early_entry": int(has_early_entry),
        "has_extended_evening": int(has_extended_evening),
        "has_special_event": int(has_special_event),
        "is_holiday": int(is_holiday),
        "is_rainy": int(is_rainy)
    }

    # API Endpoint (URL of your FastAPI app running locally or in Docker)
    API_URL = "http://localhost:8000/predict"

    try:
        with st.spinner("Calculating crowd predictions..."):
            response = requests.post(API_URL, json=payload, timeout=10)
            
        if response.status_code == 200:
            result = response.json()
            crowd_pct = result.get("predicted_crowd_level_pct", 0)
            
            st.success("Prediction Complete!")
            
            # Display Metric Box
            st.metric(
                label=f"Predicted Crowd Level for {park_name}",
                value=f"{crowd_pct:.1f}%"
            )
            
            # Visual Indicator Bar
            st.progress(min(int(crowd_pct), 100))
            
            # Contextual Advice
            if crowd_pct < 40:
                st.info("🟢 **Low Crowds Expected:** Great day to visit! Short wait times across major attractions.")
            elif crowd_pct < 70:
                st.warning("🟡 **Moderate Crowds Expected:** Moderate wait times. Consider prioritizing high-demand rides early in the morning.")
            else:
                st.error("🔴 **Heavy Crowds Expected:** Long line delays expected. Utilizing Lightning Lane / Genie+ recommended.")
                
        else:
            st.error(f"API Error ({response.status_code}): {response.text}")

    except requests.exceptions.ConnectionError:
        st.error("⚠️ Could not connect to the prediction backend API. Make sure your FastAPI app (`predict.py`) or Docker container is running on `http://localhost:8000`.")