"""
ML Trainer for Scoring Microservice
Trains and compares XGBoost and Random Forest models
Selects the best model based on cross-validation accuracy
"""

import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split, cross_val_score, StratifiedKFold
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import LabelEncoder, StandardScaler
from sklearn.metrics import classification_report, accuracy_score, confusion_matrix
import xgboost as xgb
import joblib
import json
import os
from datetime import datetime

# Paths
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_PATH = os.path.join(BASE_DIR, 'data', 'training_dataset.csv')
MODEL_PATH = os.path.join(BASE_DIR, 'models', 'scoring_model.pkl')
METRICS_PATH = os.path.join(BASE_DIR, 'models', 'training_metrics.json')


def load_and_prepare_data():
    """Load and prepare the training dataset"""
    df = pd.read_csv(DATA_PATH)
    
    # Feature engineering
    # Encode categorical variables
    packaging_encoder = LabelEncoder()
    category_encoder = LabelEncoder()
    
    df['packaging_encoded'] = packaging_encoder.fit_transform(df['packaging_type'])
    df['category_encoded'] = category_encoder.fit_transform(df['category'])
    
    # Features
    feature_cols = [
        'co2_kg', 'water_l', 'energy_mj', 
        'packaging_weight_kg', 'transport_km',
        'has_bio_label', 'has_recyclable', 'has_local_label',
        'packaging_encoded', 'category_encoded'
    ]
    
    X = df[feature_cols].values
    y = df['score_letter'].values
    
    # Encode target
    label_encoder = LabelEncoder()
    label_encoder.classes_ = np.array(['A', 'B', 'C', 'D', 'E'])
    y_encoded = label_encoder.transform(y)
    
    return X, y_encoded, label_encoder, packaging_encoder, category_encoder, feature_cols


def train_random_forest(X_train, y_train, X_test, y_test):
    """Train Random Forest model"""
    rf_model = RandomForestClassifier(
        n_estimators=200,
        max_depth=15,
        min_samples_split=5,
        min_samples_leaf=2,
        class_weight='balanced',
        random_state=42,
        n_jobs=-1
    )
    
    rf_model.fit(X_train, y_train)
    
    # Evaluate
    y_pred = rf_model.predict(X_test)
    accuracy = accuracy_score(y_test, y_pred)
    
    # Cross-validation
    cv_scores = cross_val_score(rf_model, X_train, y_train, cv=5, scoring='accuracy')
    
    return rf_model, accuracy, cv_scores.mean(), cv_scores.std()


def train_xgboost(X_train, y_train, X_test, y_test):
    """Train XGBoost model"""
    xgb_model = xgb.XGBClassifier(
        n_estimators=200,
        max_depth=8,
        learning_rate=0.1,
        subsample=0.8,
        colsample_bytree=0.8,
        min_child_weight=3,
        gamma=0.1,
        reg_alpha=0.1,
        reg_lambda=1.0,
        objective='multi:softprob',
        num_class=5,
        random_state=42,
        use_label_encoder=False,
        eval_metric='mlogloss',
        n_jobs=-1
    )
    
    xgb_model.fit(X_train, y_train)
    
    # Evaluate
    y_pred = xgb_model.predict(X_test)
    accuracy = accuracy_score(y_test, y_pred)
    
    # Cross-validation
    cv_scores = cross_val_score(xgb_model, X_train, y_train, cv=5, scoring='accuracy')
    
    return xgb_model, accuracy, cv_scores.mean(), cv_scores.std()


def train_models(verbose=True):
    """Train all models and select the best one"""
    if verbose:
        print("=" * 60)
        print("ML TRAINING - Scoring Model")
        print("=" * 60)
    
    # Load data
    X, y, label_encoder, packaging_encoder, category_encoder, feature_cols = load_and_prepare_data()
    
    if verbose:
        print(f"\n📊 Dataset: {len(X)} samples")
        print(f"   Features: {len(feature_cols)}")
        unique, counts = np.unique(y, return_counts=True)
        print(f"   Distribution: {dict(zip(label_encoder.inverse_transform(unique), counts))}")
    
    # Split data
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )
    
    if verbose:
        print(f"\n🔄 Training set: {len(X_train)} samples")
        print(f"   Test set: {len(X_test)} samples")
    
    # Train models
    if verbose:
        print("\n🌲 Training Random Forest...")
    rf_model, rf_accuracy, rf_cv_mean, rf_cv_std = train_random_forest(X_train, y_train, X_test, y_test)
    
    if verbose:
        print(f"   Test Accuracy: {rf_accuracy:.4f}")
        print(f"   CV Accuracy: {rf_cv_mean:.4f} (+/- {rf_cv_std:.4f})")
    
    if verbose:
        print("\n🚀 Training XGBoost...")
    xgb_model, xgb_accuracy, xgb_cv_mean, xgb_cv_std = train_xgboost(X_train, y_train, X_test, y_test)
    
    if verbose:
        print(f"   Test Accuracy: {xgb_accuracy:.4f}")
        print(f"   CV Accuracy: {xgb_cv_mean:.4f} (+/- {xgb_cv_std:.4f})")
    
    # Select best model (based on CV accuracy)
    if xgb_cv_mean >= rf_cv_mean:
        best_model = xgb_model
        best_name = "XGBoost"
        best_accuracy = xgb_accuracy
        best_cv_mean = xgb_cv_mean
        best_cv_std = xgb_cv_std
    else:
        best_model = rf_model
        best_name = "RandomForest"
        best_accuracy = rf_accuracy
        best_cv_mean = rf_cv_mean
        best_cv_std = rf_cv_std
    
    if verbose:
        print(f"\n✅ Best Model: {best_name}")
        print(f"   Final Accuracy: {best_accuracy:.4f}")
    
    # Detailed classification report for best model
    y_pred = best_model.predict(X_test)
    report = classification_report(y_test, y_pred, target_names=['A', 'B', 'C', 'D', 'E'], output_dict=True)
    
    if verbose:
        print("\n📈 Classification Report:")
        print(classification_report(y_test, y_pred, target_names=['A', 'B', 'C', 'D', 'E']))
    
    # Save model
    model_bundle = {
        'model': best_model,
        'model_name': best_name,
        'label_encoder': label_encoder,
        'packaging_encoder': packaging_encoder,
        'category_encoder': category_encoder,
        'feature_cols': feature_cols
    }
    
    os.makedirs(os.path.dirname(MODEL_PATH), exist_ok=True)
    joblib.dump(model_bundle, MODEL_PATH)
    
    if verbose:
        print(f"\n💾 Model saved to: {MODEL_PATH}")
    
    # Save metrics
    metrics = {
        'trained_at': datetime.now().isoformat(),
        'dataset_size': len(X),
        'train_size': len(X_train),
        'test_size': len(X_test),
        'best_model': best_name,
        'models_comparison': {
            'RandomForest': {
                'test_accuracy': float(rf_accuracy),
                'cv_accuracy_mean': float(rf_cv_mean),
                'cv_accuracy_std': float(rf_cv_std)
            },
            'XGBoost': {
                'test_accuracy': float(xgb_accuracy),
                'cv_accuracy_mean': float(xgb_cv_mean),
                'cv_accuracy_std': float(xgb_cv_std)
            }
        },
        'best_model_metrics': {
            'test_accuracy': float(best_accuracy),
            'cv_accuracy_mean': float(best_cv_mean),
            'cv_accuracy_std': float(best_cv_std),
            'classification_report': {
                k: v for k, v in report.items() 
                if k in ['A', 'B', 'C', 'D', 'E', 'macro avg', 'weighted avg']
            }
        }
    }
    
    with open(METRICS_PATH, 'w') as f:
        json.dump(metrics, f, indent=2)
    
    if verbose:
        print(f"📊 Metrics saved to: {METRICS_PATH}")
        print("\n" + "=" * 60)
        print("TRAINING COMPLETE!")
        print("=" * 60)
    
    return model_bundle, metrics


def load_model():
    """Load the trained model"""
    if not os.path.exists(MODEL_PATH):
        print("No model found. Training new model...")
        train_models()
    
    return joblib.load(MODEL_PATH)


def predict(co2_kg, water_l, energy_mj, packaging_type='plastic', 
            packaging_weight_kg=0.3, transport_km=200,
            has_bio_label=0, has_recyclable=0, has_local_label=0,
            category='processed'):
    """Make a prediction using the trained model"""
    model_bundle = load_model()
    model = model_bundle['model']
    packaging_encoder = model_bundle['packaging_encoder']
    category_encoder = model_bundle['category_encoder']
    label_encoder = model_bundle['label_encoder']
    
    # Encode inputs
    try:
        packaging_encoded = packaging_encoder.transform([packaging_type])[0]
    except ValueError:
        packaging_encoded = 0  # Default
    
    try:
        category_encoded = category_encoder.transform([category])[0]
    except ValueError:
        category_encoded = 0  # Default
    
    # Prepare features
    features = np.array([[
        co2_kg, water_l, energy_mj,
        packaging_weight_kg, transport_km,
        has_bio_label, has_recyclable, has_local_label,
        packaging_encoded, category_encoded
    ]])
    
    # Predict
    prediction = model.predict(features)[0]
    probabilities = model.predict_proba(features)[0]
    
    # Decode
    grade = label_encoder.inverse_transform([prediction])[0]
    proba_dict = {
        label_encoder.inverse_transform([i])[0]: float(p)
        for i, p in enumerate(probabilities)
    }
    
    confidence = float(max(probabilities))
    
    return {
        'grade': grade,
        'confidence': confidence,
        'probabilities': proba_dict,
        'model_name': model_bundle['model_name']
    }


if __name__ == "__main__":
    train_models(verbose=True)
