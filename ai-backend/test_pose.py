import cv2
import mediapipe as mp
import numpy as np
import sys

def test():
    video_path = "videos/badForm.mp4"
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        print(f"Failed to open {video_path}")
        return

    ret, frame = cap.read()
    if not ret:
        print("Failed to read frame")
        return

    print("Frame read successfully")
    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    
    mp_pose = mp.solutions.pose
    with mp_pose.Pose(static_image_mode=True, min_detection_confidence=0.5) as pose:
        results = pose.process(rgb)
        if results.pose_landmarks:
            print(f"Pose detected! Found {len(results.pose_landmarks.landmark)} landmarks")
        else:
            print("No pose detected in first frame")

if __name__ == "__main__":
    test()
