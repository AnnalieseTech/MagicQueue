import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error, mean_absolute_error
import xgboost as xgb
import joblib

print("1. Loading data...")
df = pd.read_csv('data/calendar_enriched.csv')

print("2. Preparing data and features...")
df['operating_minutes'] = df['operating_minutes'].fillna(df['operating_minutes'].median())

features = [
    'park_name', 'month', 'dow_number', 'is_weekend', 
    'operating_minutes', 'has_early_entry', 'has_extended_evening', 
    'has_special_event', 'is_holiday', 'is_rainy'
]
target = 'crowd_level_pct'

X = df[features]
y = df[target]

# One-hot encoding
X_encoded = pd.get_dummies(X, columns=['park_name'], drop_first=True)

# Train/Validation split
X_train, X_val, y_train, y_val = train_test_split(X_encoded, y, test_size=0.2, random_state=42)

print("3. Training the best model (XGBoost)...")
# Using the winning parameters from your notebook tuning
final_model = xgb.XGBRegressor(learning_rate=0.1, max_depth=6, n_estimators=100, random_state=42)
final_model.fit(X_train, y_train)

# Evaluate
preds = final_model.predict(X_val)
rmse = np.sqrt(mean_squared_error(y_val, preds))
mae = mean_absolute_error(y_val, preds)
print(f"Validation Results -> RMSE: {rmse:.4f} | MAE: {mae:.4f}")

print("4. Saving the model artifact...")
joblib.dump(final_model, 'model.bin')
print("Model saved successfully as 'model.bin'!")