"""
ML Imputer for LCA-Lite Microservice
XGBoost Regressor for CO₂ estimation when ingredient factors are unknown
"""

import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
import xgboost as xgb
import joblib
import json
import os
from datetime import datetime

# Paths
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_PATH = os.path.join(BASE_DIR, 'data', 'co2_training.csv')
MODEL_PATH = os.path.join(BASE_DIR, 'data', 'co2_imputer.pkl')
METRICS_PATH = os.path.join(BASE_DIR, 'data', 'imputer_metrics.json')


def load_and_prepare_data():
    """Load and prepare the CO₂ training dataset"""
    df = pd.read_csv(DATA_PATH)
    
    # Encode packaging type
    packaging_encoder = LabelEncoder()
    df['packaging_encoded'] = packaging_encoder.fit_transform(df['packaging_type'])
    
    # Features
    feature_cols = [
        'num_ingredients', 'total_weight_kg', 
        'has_meat', 'has_dairy', 'has_vegetables',
        'packaging_encoded', 'packaging_weight_kg', 'transport_km'
    ]
    
    X = df[feature_cols].values
    y = df['total_co2_kg'].values
    
    return X, y, packaging_encoder, feature_cols


def train_co2_model(verbose=True):
    """Train XGBoost regressor for CO₂ estimation"""
    if verbose:
        print("=" * 60)
        print("ML TRAINING - CO₂ Imputation Model")
        print("=" * 60)
    
    # Load data
    X, y, packaging_encoder, feature_cols = load_and_prepare_data()
    
    if verbose:
        print(f"\n📊 Dataset: {len(X)} samples")
        print(f"   Features: {len(feature_cols)}")
        print(f"   CO₂ range: {y.min():.2f} - {y.max():.2f} kg")
    
    # Split data
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )
    
    if verbose:
        print(f"\n🔄 Training set: {len(X_train)} samples")
        print(f"   Test set: {len(X_test)} samples")
    
    # Train XGBoost Regressor
    if verbose:
        print("\n🚀 Training XGBoost Regressor...")
    
    model = xgb.XGBRegressor(
        n_estimators=200,
        max_depth=6,
        learning_rate=0.1,
        subsample=0.8,
        colsample_bytree=0.8,
        min_child_weight=3,
        gamma=0.1,
        reg_alpha=0.1,
        reg_lambda=1.0,
        random_state=42,
        n_jobs=-1
    )
    
    model.fit(X_train, y_train)
    
    # Evaluate
    y_pred = model.predict(X_test)
    
    mae = mean_absolute_error(y_test, y_pred)
    rmse = np.sqrt(mean_squared_error(y_test, y_pred))
    r2 = r2_score(y_test, y_pred)
    
    # Cross-validation
    cv_scores = cross_val_score(model, X_train, y_train, cv=5, scoring='r2')
    
    if verbose:
        print(f"\n📈 Test Metrics:")
        print(f"   MAE: {mae:.4f} kg CO₂")
        print(f"   RMSE: {rmse:.4f} kg CO₂")
        print(f"   R² Score: {r2:.4f}")
        print(f"   CV R² Score: {cv_scores.mean():.4f} (+/- {cv_scores.std():.4f})")
    
    # Feature importance
    feature_importance = dict(zip(feature_cols, model.feature_importances_.tolist()))
    
    if verbose:
        print("\n🎯 Feature Importance:")
        for name, imp in sorted(feature_importance.items(), key=lambda x: -x[1]):
            print(f"   {name}: {imp:.3f}")
    
    # Save model
    model_bundle = {
        'model': model,
        'packaging_encoder': packaging_encoder,
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
        'model': 'XGBoost Regressor',
        'metrics': {
            'mae': float(mae),
            'rmse': float(rmse),
            'r2_score': float(r2),
            'cv_r2_mean': float(cv_scores.mean()),
            'cv_r2_std': float(cv_scores.std())
        },
        'feature_importance': feature_importance,
        'co2_range': {
            'min': float(y.min()),
            'max': float(y.max()),
            'mean': float(y.mean())
        }
    }
    
    with open(METRICS_PATH, 'w') as f:
        json.dump(metrics, f, indent=2)
    
    if verbose:
        print(f"📊 Metrics saved to: {METRICS_PATH}")
        print("\n" + "=" * 60)
        print("TRAINING COMPLETE!")
        print(f"R² Score: {r2:.4f} - {'✅ Good' if r2 >= 0.80 else '⚠️ Needs improvement'}")
        print("=" * 60)
    
    return model_bundle, metrics


def load_co2_model():
    """Load the trained CO₂ model"""
    if not os.path.exists(MODEL_PATH):
        print("No CO₂ model found. Training new model...")
        train_co2_model()
    
    return joblib.load(MODEL_PATH)


def estimate_co2(num_ingredients: int, total_weight_kg: float,
                 has_meat: bool = False, has_dairy: bool = False, 
                 has_vegetables: bool = False,
                 packaging_type: str = 'plastic', 
                 packaging_weight_kg: float = 0.2,
                 transport_km: float = 200) -> dict:
    """
    Estimate CO₂ emissions when ingredient factors are unknown.
    
    Returns:
        dict with 'co2_kg', 'confidence', and 'is_estimated'
    """
    model_bundle = load_co2_model()
    model = model_bundle['model']
    packaging_encoder = model_bundle['packaging_encoder']
    
    # Encode packaging
    try:
        packaging_encoded = packaging_encoder.transform([packaging_type])[0]
    except ValueError:
        packaging_encoded = 0  # Default to first category
    
    # Prepare features
    features = np.array([[
        num_ingredients, total_weight_kg,
        int(has_meat), int(has_dairy), int(has_vegetables),
        packaging_encoded, packaging_weight_kg, transport_km
    ]])
    
    # Predict
    co2_prediction = model.predict(features)[0]
    
    # Estimate confidence based on input characteristics
    # Higher confidence for typical inputs
    confidence = 0.85
    if has_meat:
        confidence = 0.90  # Meat products are well-represented
    elif has_vegetables and not has_dairy:
        confidence = 0.88
    
    # Lower confidence for extreme values
    if transport_km > 1000 or total_weight_kg > 3:
        confidence -= 0.10
    
    return {
        'co2_kg': round(float(max(0, co2_prediction)), 3),
        'confidence': round(confidence, 2),
        'is_estimated': True,
        'model': 'XGBoost CO₂ Regressor'
    }


def test_imputer():
    """Test the CO₂ imputer with sample inputs"""
    print("\n🧪 Testing CO₂ Imputer...")
    
    test_cases = [
        {'num_ingredients': 3, 'total_weight_kg': 0.6, 'has_vegetables': True, 
         'packaging_type': 'paper', 'transport_km': 50},
        {'num_ingredients': 4, 'total_weight_kg': 1.0, 'has_dairy': True,
         'packaging_type': 'plastic', 'transport_km': 200},
        {'num_ingredients': 5, 'total_weight_kg': 1.5, 'has_meat': True,
         'packaging_type': 'plastic', 'transport_km': 400},
        {'num_ingredients': 6, 'total_weight_kg': 1.8, 'has_meat': True, 'has_dairy': True,
         'packaging_type': 'aluminum', 'transport_km': 450},
    ]
    
    for i, tc in enumerate(test_cases, 1):
        result = estimate_co2(**tc)
        print(f"\nTest {i}: {tc}")
        print(f"  → CO₂: {result['co2_kg']:.2f} kg (confidence: {result['confidence']:.0%})")
    
    print("\n✅ Imputer tests completed!")


if __name__ == "__main__":
    train_co2_model(verbose=True)
    test_imputer()
