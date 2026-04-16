import cv2
import mediapipe as mp
import numpy as np

def calculate_angle(a, b, c):
    a = np.array(a)
    b = np.array(b)
    c = np.array(c)
    
    radians = np.arctan2(c[1]-b[1], c[0]-b[0]) - np.arctan2(a[1]-b[1], a[0]-b[0])
    angle = np.abs(radians*180.0/np.pi)
    
    if angle > 180.0:
        angle = 360 - angle
        
    return angle

def main():
    mp_pose = mp.solutions.pose
    mp_drawing = mp.solutions.drawing_utils
    
    video_path = "test.mp4"
    cap = cv2.VideoCapture(video_path)
    
    if not cap.isOpened():
        print(f"Could not open {video_path}")
        return

    total_frames = 0
    pose_frames = 0
    knee_angles = []

    # Initialize MediaPipe Pose
    with mp_pose.Pose(min_detection_confidence=0.5, min_tracking_confidence=0.5) as pose:
        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break
                
            total_frames += 1
            
            # Recolor image to RGB
            rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            rgb.flags.writeable = False
            
            # Make detection
            results = pose.process(rgb)
            
            # Recolor back to BGR for display
            rgb.flags.writeable = True
            frame = cv2.cvtColor(rgb, cv2.COLOR_RGB2BGR)
            
            if results.pose_landmarks:
                pose_frames += 1
                
                # Draw landmarks on frame
                mp_drawing.draw_landmarks(
                    frame, results.pose_landmarks, mp_pose.POSE_CONNECTIONS,
                    mp_drawing.DrawingSpec(color=(245,117,66), thickness=2, circle_radius=2),
                    mp_drawing.DrawingSpec(color=(245,66,230), thickness=2, circle_radius=2)
                )
                
                landmarks = results.pose_landmarks.landmark
                
                # Left Knee Coordinate Mapping: Hip (23), Knee (25), Ankle (27)
                hip = [landmarks[mp_pose.PoseLandmark.LEFT_HIP.value].x, 
                       landmarks[mp_pose.PoseLandmark.LEFT_HIP.value].y]
                knee = [landmarks[mp_pose.PoseLandmark.LEFT_KNEE.value].x, 
                        landmarks[mp_pose.PoseLandmark.LEFT_KNEE.value].y]
                ankle = [landmarks[mp_pose.PoseLandmark.LEFT_ANKLE.value].x, 
                         landmarks[mp_pose.PoseLandmark.LEFT_ANKLE.value].y]
                
                # Compute angle
                angle = calculate_angle(hip, knee, ankle)
                knee_angles.append(angle)
            else:
                print(f"NO POSE DETECTED on frame {total_frames}")

            # Show Display Debug
            cv2.imshow("Pose Debug - Press 'q' to exit", frame)
            
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

    cap.release()
    cv2.destroyAllWindows()

    print("\n--- RESULTS ---")
    print(f"Total frames: {total_frames}")
    print(f"Frames with pose detected: {pose_frames}")
    
    if pose_frames == 0:
        print("NO POSE DETECTED")
    else:
        # Prevent accessing beyond list length if < 5 frames processed
        print(f"First 5 knee angles: {[round(a, 2) for a in knee_angles[:5]]}")
        if len(knee_angles) > 1:
            print(f"Standard deviation of angles: {np.std(knee_angles):.2f}")
        else:
            print("Standard deviation of angles: N/A")

if __name__ == "__main__":
    main()
