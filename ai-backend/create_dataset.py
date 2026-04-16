import os
import glob
import pandas as pd
import numpy as np
from app.services import pose_service

def extract_video_features(video_path):
    # Run existing physical feature extraction pipeline
    pose_service.analyze_video_form(video_path)
    
    if not pose_service.FRAME_ANGLES_HISTORY:
        print(f"Failed to extract pose for {video_path}")
        return None
        
    knee_angles = [f["knee"] for f in pose_service.FRAME_ANGLES_HISTORY if "knee" in f]
    hip_angles = [f["hip"] for f in pose_service.FRAME_ANGLES_HISTORY if "hip" in f]
    back_angles = [f["back"] for f in pose_service.FRAME_ANGLES_HISTORY if "back" in f]
    
    if len(knee_angles) == 0:
        return None
        
    knee_arr = np.array(knee_angles)
    
    knee_std = round(float(np.std(knee_arr)), 4)
    depth = round(float(np.min(knee_arr)), 2)
    smoothness = round(1.0 / (knee_std + 1e-6), 4)
    
    hip_std = round(float(np.std(np.array(hip_angles))), 4) if hip_angles else 0.0
    back_std = round(float(np.std(np.array(back_angles))), 4) if back_angles else 0.0
    
    return {
        "knee_std": knee_std,
        "hip_std": hip_std,
        "back_std": back_std,
        "depth": depth,
        "smoothness": smoothness
    }

def main():
    videos = glob.glob("videos/*.mp4")
    data = []
    
    if not videos:
        print("No .mp4 files found in videos/ directory.")
        return
        
    for vid in videos:
        filename = os.path.basename(vid).lower()
        if "good" in filename:
            label = 0
        elif "bad" in filename:
            label = 1
        else:
            print(f"Skipping {vid} - no 'good' or 'bad' tag in filename.")
            continue
            
        print(f"Processing {vid}...")
        features = extract_video_features(vid)
        if features:
            features['label'] = label
            data.append(features)
            
    if data:
        df = pd.DataFrame(data)
        df.to_csv("dataset.csv", index=False)
        print(f"\nDataset successfully generated with {len(data)} records saving to dataset.csv!")
    else:
        print("No valid data could be constructed.")

if __name__ == "__main__":
    main()
