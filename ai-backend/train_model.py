import pandas as pd
import joblib
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score

def main():
    try:
        df = pd.read_csv("dataset.csv")
    except FileNotFoundError:
        print("Error: dataset.csv not found. Please run create_dataset.py first!")
        return
        
    required_cols = ["knee_std", "hip_std", "back_std", "depth", "smoothness", "label"]
    if not all(col in df.columns for col in required_cols):
        print("Error: dataset.csv is missing required columns structure.")
        return
        
    X = df[["knee_std", "hip_std", "back_std", "depth", "smoothness"]]
    y = df["label"]
    
    if len(df) < 2:
        print("Error: Dataset requires at least 2 entries to train.")
        return
        
    # Dynamically scale test_size if dataset is tiny to prevent crashing
    test_size = 0.2 if len(df) >= 5 else 0.5
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=test_size, random_state=42)
    
    print(f"Training RandomForestClassifier on {len(X_train)} samples...")
    model = RandomForestClassifier(n_estimators=100, max_depth=5, random_state=42)
    model.fit(X_train, y_train)
    
    y_pred = model.predict(X_test)
    accuracy = accuracy_score(y_test, y_pred)
    
    print(f"Model trained successfully!")
    print(f"Validation Accuracy: {accuracy * 100:.2f}%")
    
    joblib.dump(model, "model.pkl")
    print("Model saved to model.pkl")

if __name__ == "__main__":
    main()
