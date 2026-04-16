from __future__ import annotations

import os
import sys
import pandas as pd
import numpy as np
import cv2
import logging

# Setup pathing
_SERVICES_DIR = os.path.dirname(os.path.abspath(__file__))
_BACKEND_DIR  = os.path.abspath(os.path.join(_SERVICES_DIR, "..", ".."))
if _BACKEND_DIR not in sys.path:
    sys.path.insert(0, _BACKEND_DIR)

from app.services.pose_service import PoseService, calculate_angle
from app.services.generate_dataset import engineer_features

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

VIDEO_DIR = os.path.join(_BACKEND_DIR, "videos")
OUT_CSV   = os.path.join(_BACKEND_DIR, "data", "real_world_features.csv")

def extract_features_from_video(video_path: str) -> dict | None:
    """Extracts mean biomechanical metrics from a video file."""
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        return None

    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    max_samples = 20
    stride = max(1, total_frames // max_samples)

    knee_angles = []
    hip_angles  = []
    back_angles = []
    drifts      = []
    
    try:
        with PoseService() as svc:
            for i in range(max_samples):
                frame_idx = i * stride
                if frame_idx >= total_frames: break
                
                cap.set(cv2.CAP_PROP_POS_FRAMES, frame_idx)
                ret, frame = cap.read()
                if not ret: break

                rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                landmarks = svc.process_frame(rgb)
                if not landmarks: continue

                lm_map = {lm.name: lm for lm in landmarks}
                hip   = lm_map.get("LEFT_HIP")
                knee  = lm_map.get("LEFT_KNEE")
                ankle = lm_map.get("LEFT_ANKLE")
                shoulder = lm_map.get("LEFT_SHOULDER")

                if not (hip and knee and ankle and shoulder): continue

                # Knee Flexion
                ka = calculate_angle((hip.x, hip.y, hip.z), (knee.x, knee.y, knee.z), (ankle.x, ankle.y, ankle.z))
                # Hip Flexion
                ha = calculate_angle((shoulder.x, shoulder.y, shoulder.z), (hip.x, hip.y, hip.z), (knee.x, knee.y, knee.z))
                # Back Angle
                ba = calculate_angle((shoulder.x, shoulder.y, shoulder.z), (hip.x, hip.y, hip.z), (knee.x, knee.y, knee.z))
                
                knee_angles.append(ka)
                hip_angles.append(ha)
                back_angles.append(ba)
                drifts.append(abs(knee.x - ankle.x))
    finally:
        cap.release()

    if not knee_angles: return None

    # Calculate aggregate metrics
    return {
        "knee_std": np.std(knee_angles),
        "hip_std":  np.std(hip_angles),
        "back_std": np.std(back_angles),
        "avg_drift": np.mean(drifts),
        "form_decay": (np.std(knee_angles) * 2.0) / 100.0, # Normalised 0-1
    }

def process_all_videos():
    if not os.path.exists(VIDEO_DIR):
        logger.error(f"Video directory {VIDEO_DIR} not found.")
        return

    data = []
    for filename in os.listdir(VIDEO_DIR):
        if not filename.endswith((".mp4", ".mov", ".avi")): continue
        
        path = os.path.join(VIDEO_DIR, filename)
        logger.info(f"Processing {filename}...")
        
        features = extract_features_from_video(path)
        if features:
            # Assign label based on filename
            name_lower = filename.lower()
            if "good" in name_lower:
                risk = 15.0 + np.random.uniform(-5, 5)
                load = 4.0
                fatigue = 3.0
                recovery = 85.0
            elif "bad" in name_lower:
                risk = 80.0 + np.random.uniform(-5, 5)
                load = 8.5
                fatigue = 8.0
                recovery = 30.0
            else:
                # Default case for WhatsApp videos - simple heuristic based on detected decay
                decay = features["form_decay"]
                risk = 40.0 + (decay * 50.0) # Scale risk between 40-90
                load = 6.0
                fatigue = 5.0
                recovery = 60.0

            row = {
                "video": filename,
                "training_load": load,
                "recovery_score": recovery,
                "fatigue_index": fatigue,
                "form_decay": round(features["form_decay"], 4),
                "previous_injury": 0,
                "injury_risk": round(risk, 2),
                **features
            }
            data.append(row)

    if not data:
        logger.warning("No data extracted from videos.")
        return

    df = pd.DataFrame(data)
    
    # Augment data to reach ~100 samples
    augmented_rows = []
    for _ in range(10): # 10x augmentation
        for _, row in df.iterrows():
            new_row = row.copy()
            # Add subtle noise to features and target
            new_row["form_decay"] = max(0, min(1, row["form_decay"] + np.random.normal(0, 0.05)))
            new_row["injury_risk"] = max(0, min(100, row["injury_risk"] + np.random.normal(0, 3)))
            new_row["knee_std"] *= np.random.uniform(0.9, 1.1)
            augmented_rows.append(new_row)
            
    final_df = pd.concat([df, pd.DataFrame(augmented_rows)], ignore_index=True)
    final_df.to_csv(OUT_CSV, index=False)
    logger.info(f"Dataset with {len(final_df)} samples saved to {OUT_CSV}")

if __name__ == "__main__":
    process_all_videos()
