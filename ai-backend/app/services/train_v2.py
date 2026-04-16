from __future__ import annotations

import os
import sys
import joblib
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.preprocessing import MinMaxScaler
from sklearn.model_selection import train_test_split
from xgboost import XGBRegressor

_SERVICES_DIR = os.path.dirname(os.path.abspath(__file__))
_BACKEND_DIR  = os.path.abspath(os.path.join(_SERVICES_DIR, "..", ".."))
_DATA_DIR     = os.path.join(_BACKEND_DIR, "data")

REAL_DATA_PATH = os.path.join(_DATA_DIR, "real_world_features.csv")
MODEL_DIR      = _DATA_DIR

RANDOM_SEED = 42
np.random.seed(RANDOM_SEED)

def load_combined_data() -> pd.DataFrame:
    # 1. Load Real Data
    if not os.path.exists(REAL_DATA_PATH):
        raise FileNotFoundError(f"Real data not found at {REAL_DATA_PATH}. Run video_to_dataset.py first.")
    
    real_df = pd.read_csv(REAL_DATA_PATH)
    # Drop non-feature columns if present
    drop_cols = ["video", "knee_std", "hip_std", "back_std", "avg_drift"]
    real_df = real_df.drop(columns=[c for c in drop_cols if c in real_df.columns])

    # 2. Generate Synthetic Baseline (to provide variety in load/fatigue)
    from app.services.generate_dataset import generate_raw_dataset, engineer_features
    synth_raw = generate_raw_dataset(n_samples=300)
    synth_df = engineer_features(synth_raw)

    # 3. Combine
    combined = pd.concat([real_df, synth_df], ignore_index=True)
    return combined

def train_and_evaluate():
    df = load_combined_data()
    
    feature_cols = [c for c in df.columns if c != "injury_risk"]
    X = df[feature_cols]
    y = df["injury_risk"]

    # Scale
    scaler = MinMaxScaler()
    X_scaled = scaler.fit_transform(X)
    X_df = pd.DataFrame(X_scaled, columns=feature_cols)

    X_train, X_test, y_train, y_test = train_test_split(X_df, y, test_size=0.2, random_state=RANDOM_SEED)

    # Models
    xgb = XGBRegressor(n_estimators=100, max_depth=4, learning_rate=0.1, random_state=RANDOM_SEED)
    rf  = RandomForestRegressor(n_estimators=100, max_depth=6, random_state=RANDOM_SEED)

    xgb.fit(X_train, y_train)
    rf.fit(X_train, y_train)

    # Evaluation
    xgb_preds = np.clip(xgb.predict(X_test), 0, 100)
    rf_preds  = np.clip(rf.predict(X_test), 0, 100)

    metrics = {
        "XGBoost": {
            "RMSE": np.sqrt(mean_squared_error(y_test, xgb_preds)),
            "MAE": mean_absolute_error(y_test, xgb_preds),
            "R2": r2_score(y_test, xgb_preds)
        },
        "RandomForest": {
            "RMSE": np.sqrt(mean_squared_error(y_test, rf_preds)),
            "MAE": mean_absolute_error(y_test, rf_preds),
            "R2": r2_score(y_test, rf_preds)
        }
    }

    # Save
    os.makedirs(MODEL_DIR, exist_ok=True)
    joblib.dump(xgb, os.path.join(MODEL_DIR, "xgboost.pkl"))
    joblib.dump(rf, os.path.join(MODEL_DIR, "random_forest.pkl"))
    joblib.dump(scaler, os.path.join(MODEL_DIR, "scaler.pkl"))

    print("\n=== Training Results (Real + Synthetic) ===")
    for model_name, m in metrics.items():
        print(f"{model_name}: RMSE={m['RMSE']:.2f}, MAE={m['MAE']:.2f}, R2={m['R2']:.2f}")

if __name__ == "__main__":
    train_and_evaluate()
