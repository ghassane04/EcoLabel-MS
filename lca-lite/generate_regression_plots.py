"""
Script to generate visualization for CO₂ Regression Model (LCA-Lite)
Since it's regression, we create:
1. Predicted vs Actual scatter plot
2. Residual distribution
"""

import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
import xgboost as xgb
import matplotlib.pyplot as plt
from sklearn.preprocessing import LabelEncoder
import os

# Paths
DATA_PATH = 'data/co2_training.csv'

def generate_regression_plots():
    print("=" * 60)
    print("Generating Regression Plots for CO₂ Imputation Model")
    print("=" * 60)
    
    # Load data
    df = pd.read_csv(DATA_PATH)
    print(f"\n📊 Dataset loaded: {len(df)} samples")
    
    # Encode packaging
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
    
    print(f"   CO₂ range: {y.min():.2f} - {y.max():.2f} kg")
    
    # Split
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )
    
    # Train XGBoost
    print("\n🚀 Training XGBoost Regressor...")
    model = xgb.XGBRegressor(
        n_estimators=200,
        max_depth=6,
        learning_rate=0.1,
        random_state=42
    )
    model.fit(X_train, y_train)
    
    # Predict
    y_pred = model.predict(X_test)
    
    # Metrics
    mae = mean_absolute_error(y_test, y_pred)
    rmse = np.sqrt(mean_squared_error(y_test, y_pred))
    r2 = r2_score(y_test, y_pred)
    
    print(f"\n📈 Metrics:")
    print(f"   MAE: {mae:.4f} kg")
    print(f"   RMSE: {rmse:.4f} kg")
    print(f"   R² Score: {r2:.4f}")
    
    # Create figure with 2 subplots
    fig, axes = plt.subplots(1, 2, figsize=(14, 6))
    
    # 1. Predicted vs Actual
    ax1 = axes[0]
    ax1.scatter(y_test, y_pred, alpha=0.6, c='steelblue', edgecolors='white', s=60)
    
    # Perfect prediction line
    min_val = min(y_test.min(), y_pred.min())
    max_val = max(y_test.max(), y_pred.max())
    ax1.plot([min_val, max_val], [min_val, max_val], 'r--', lw=2, label='Prédiction parfaite')
    
    ax1.set_xlabel('CO₂ Réel (kg)', fontsize=12)
    ax1.set_ylabel('CO₂ Prédit (kg)', fontsize=12)
    ax1.set_title(f'Prédiction vs Réalité - CO₂\n(R² = {r2:.3f})', fontsize=14, fontweight='bold')
    ax1.legend()
    ax1.grid(True, alpha=0.3)
    
    # 2. Residuals distribution
    ax2 = axes[1]
    residuals = y_test - y_pred
    
    ax2.hist(residuals, bins=20, color='green', alpha=0.7, edgecolor='white')
    ax2.axvline(x=0, color='red', linestyle='--', lw=2, label='Erreur = 0')
    ax2.axvline(x=residuals.mean(), color='orange', linestyle='-', lw=2, 
                label=f'Moyenne = {residuals.mean():.3f}')
    
    ax2.set_xlabel('Résidu (Réel - Prédit)', fontsize=12)
    ax2.set_ylabel('Fréquence', fontsize=12)
    ax2.set_title(f'Distribution des Résidus\n(MAE = {mae:.3f} kg)', fontsize=14, fontweight='bold')
    ax2.legend()
    ax2.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig('co2_regression_analysis.png', dpi=300, bbox_inches='tight', facecolor='white')
    print(f"\n💾 Saved to: co2_regression_analysis.png")
    
    # Feature importance
    fig2, ax = plt.subplots(figsize=(10, 6))
    importance = model.feature_importances_
    indices = np.argsort(importance)[::-1]
    
    colors = plt.cm.Greens(np.linspace(0.4, 0.9, len(feature_cols)))
    ax.barh(range(len(feature_cols)), importance[indices], color=colors)
    ax.set_yticks(range(len(feature_cols)))
    ax.set_yticklabels([feature_cols[i] for i in indices])
    ax.invert_yaxis()
    ax.set_xlabel('Importance', fontsize=12)
    ax.set_title('Importance des Features - Modèle CO₂', fontsize=14, fontweight='bold')
    
    plt.tight_layout()
    plt.savefig('co2_feature_importance.png', dpi=300, bbox_inches='tight', facecolor='white')
    print(f"💾 Saved to: co2_feature_importance.png")
    
    print("\n" + "=" * 60)
    print("DONE!")
    print("=" * 60)


if __name__ == "__main__":
    generate_regression_plots()
