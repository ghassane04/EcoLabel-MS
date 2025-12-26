"""
ML Model Training Script for EcoLabel Scoring
Trains a Random Forest classifier to predict eco-scores (A-E)

Features:
- Preprocessing: StandardScaler, OneHotEncoder
- Models tested: Logistic Regression, Random Forest, Gradient Boosting
- Evaluation: Accuracy, F1-score, Confusion Matrix
- Saves the best model with joblib
"""

import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.preprocessing import StandardScaler, LabelEncoder, OneHotEncoder
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, f1_score, confusion_matrix, classification_report
import joblib
import os
import json

# ============ CONFIGURATION ============
DATA_PATH = os.path.join(os.path.dirname(__file__), '..', 'data', 'training_dataset.csv')
MODEL_PATH = os.path.join(os.path.dirname(__file__), '..', 'models', 'scoring_model.pkl')
SCALER_PATH = os.path.join(os.path.dirname(__file__), '..', 'models', 'preprocessing_pipeline.pkl')
METRICS_PATH = os.path.join(os.path.dirname(__file__), '..', 'models', 'training_metrics.json')

# Feature columns
NUMERIC_FEATURES = ['co2_kg', 'water_l', 'energy_mj', 'packaging_weight_kg', 'transport_km']
CATEGORICAL_FEATURES = ['packaging_type', 'category']
BINARY_FEATURES = ['has_bio_label', 'has_recyclable', 'has_local_label']
TARGET = 'score_letter'

# Score mappings for probability-weighted scoring
SCORE_VALUES = {'A': 95, 'B': 75, 'C': 55, 'D': 35, 'E': 15}


def load_and_preprocess_data():
    """Load and prepare the dataset"""
    print("=" * 60)
    print("ETAPE 1: CHARGEMENT ET PREPROCESSING DES DONNEES")
    print("=" * 60)
    
    df = pd.read_csv(DATA_PATH)
    print(f"Dataset chargé: {len(df)} lignes, {len(df.columns)} colonnes")
    print(f"\nColonnes: {list(df.columns)}")
    print(f"\nDistribution des scores:")
    print(df[TARGET].value_counts().sort_index())
    
    # Check for missing values
    missing = df.isnull().sum()
    if missing.any():
        print(f"\nValeurs manquantes détectées:\n{missing[missing > 0]}")
        df = df.dropna()
        print(f"Après nettoyage: {len(df)} lignes")
    else:
        print("\nAucune valeur manquante ✓")
    
    return df


def create_preprocessing_pipeline():
    """Create sklearn preprocessing pipeline"""
    print("\n" + "=" * 60)
    print("ETAPE 2: CREATION DU PIPELINE DE PREPROCESSING")
    print("=" * 60)
    
    # Column transformer for different feature types
    preprocessor = ColumnTransformer(
        transformers=[
            ('num', StandardScaler(), NUMERIC_FEATURES),
            ('cat', OneHotEncoder(drop='first', sparse_output=False, handle_unknown='ignore'), CATEGORICAL_FEATURES),
            ('bin', 'passthrough', BINARY_FEATURES)
        ],
        remainder='drop'
    )
    
    print("Pipeline créé avec:")
    print(f"  - StandardScaler pour: {NUMERIC_FEATURES}")
    print(f"  - OneHotEncoder pour: {CATEGORICAL_FEATURES}")
    print(f"  - Passthrough pour: {BINARY_FEATURES}")
    
    return preprocessor


def train_and_evaluate_models(X_train, X_test, y_train, y_test, preprocessor):
    """Train multiple models and compare performance"""
    print("\n" + "=" * 60)
    print("ETAPE 3: ENTRAINEMENT ET EVALUATION DES MODELES")
    print("=" * 60)
    
    # Define models to test
    models = {
        'Logistic Regression': LogisticRegression(max_iter=1000, random_state=42),
        'Random Forest': RandomForestClassifier(n_estimators=100, max_depth=10, random_state=42),
        'Gradient Boosting': GradientBoostingClassifier(n_estimators=100, max_depth=5, random_state=42)
    }
    
    results = {}
    best_model = None
    best_accuracy = 0
    best_name = ""
    
    for name, model in models.items():
        print(f"\n--- {name} ---")
        
        # Create full pipeline
        pipeline = Pipeline([
            ('preprocessor', preprocessor),
            ('classifier', model)
        ])
        
        # Train
        pipeline.fit(X_train, y_train)
        
        # Predict
        y_pred = pipeline.predict(X_test)
        
        # Metrics
        accuracy = accuracy_score(y_test, y_pred)
        f1 = f1_score(y_test, y_pred, average='macro')
        
        # Cross-validation
        cv_scores = cross_val_score(pipeline, X_train, y_train, cv=5, scoring='accuracy')
        
        results[name] = {
            'accuracy': float(accuracy),
            'f1_score': float(f1),
            'cv_mean': float(cv_scores.mean()),
            'cv_std': float(cv_scores.std())
        }
        
        print(f"  Accuracy: {accuracy:.2%}")
        print(f"  F1-Score (macro): {f1:.2%}")
        print(f"  Cross-Val (5-fold): {cv_scores.mean():.2%} (+/- {cv_scores.std()*2:.2%})")
        
        if accuracy > best_accuracy:
            best_accuracy = accuracy
            best_model = pipeline
            best_name = name
    
    print("\n" + "=" * 60)
    print(f"MEILLEUR MODELE: {best_name}")
    print(f"Accuracy: {best_accuracy:.2%}")
    print("=" * 60)
    
    return best_model, best_name, results


def generate_confusion_matrix(model, X_test, y_test):
    """Generate and display confusion matrix"""
    print("\n" + "=" * 60)
    print("ETAPE 4: MATRICE DE CONFUSION")
    print("=" * 60)
    
    y_pred = model.predict(X_test)
    labels = ['A', 'B', 'C', 'D', 'E']
    
    cm = confusion_matrix(y_test, y_pred, labels=labels)
    
    print("\nMatrice de confusion:")
    print("     ", "  ".join(labels))
    for i, row in enumerate(cm):
        print(f"  {labels[i]}: {row}")
    
    print("\nRapport de classification:")
    print(classification_report(y_test, y_pred, labels=labels, zero_division=0))
    
    return cm.tolist()


def get_feature_importance(model):
    """Extract feature importance from Random Forest"""
    print("\n" + "=" * 60)
    print("ETAPE 5: IMPORTANCE DES FEATURES")
    print("=" * 60)
    
    try:
        classifier = model.named_steps['classifier']
        if hasattr(classifier, 'feature_importances_'):
            importances = classifier.feature_importances_
            
            # Get feature names after transformation
            preprocessor = model.named_steps['preprocessor']
            
            # Build feature names
            feature_names = NUMERIC_FEATURES.copy()
            
            # Add one-hot encoded names
            cat_encoder = preprocessor.named_transformers_['cat']
            for i, cat in enumerate(CATEGORICAL_FEATURES):
                cats = cat_encoder.categories_[i][1:]  # skip first due to drop='first'
                feature_names.extend([f"{cat}_{c}" for c in cats])
            
            feature_names.extend(BINARY_FEATURES)
            
            # Sort by importance
            indices = np.argsort(importances)[::-1]
            
            print("\nTop 10 features par importance:")
            importance_dict = {}
            for i, idx in enumerate(indices[:10]):
                if idx < len(feature_names):
                    name = feature_names[idx]
                    imp = importances[idx]
                    importance_dict[name] = float(imp)
                    print(f"  {i+1}. {name}: {imp:.4f}")
            
            return importance_dict
    except Exception as e:
        print(f"Impossible d'extraire l'importance: {e}")
    
    return {}


def save_model_and_metrics(model, model_name, results, confusion_mat, feature_imp):
    """Save the trained model and metrics"""
    print("\n" + "=" * 60)
    print("ETAPE 6: SAUVEGARDE DU MODELE")
    print("=" * 60)
    
    # Create models directory
    os.makedirs(os.path.dirname(MODEL_PATH), exist_ok=True)
    
    # Save model
    joblib.dump(model, MODEL_PATH)
    print(f"Modèle sauvegardé: {MODEL_PATH}")
    
    # Save metrics
    metrics = {
        'best_model': model_name,
        'all_results': results,
        'confusion_matrix': confusion_mat,
        'feature_importance': feature_imp,
        'features': {
            'numeric': NUMERIC_FEATURES,
            'categorical': CATEGORICAL_FEATURES,
            'binary': BINARY_FEATURES
        }
    }
    
    with open(METRICS_PATH, 'w') as f:
        json.dump(metrics, f, indent=2)
    print(f"Métriques sauvegardées: {METRICS_PATH}")


def main():
    """Main training pipeline"""
    print("\n" + "=" * 60)
    print("   ENTRAINEMENT DU MODELE DE SCORING ECOLABEL")
    print("   Machine Learning Supervisé - Classification")
    print("=" * 60 + "\n")
    
    # 1. Load data
    df = load_and_preprocess_data()
    
    # 2. Split features and target
    X = df[NUMERIC_FEATURES + CATEGORICAL_FEATURES + BINARY_FEATURES]
    y = df[TARGET]
    
    # Encode target
    label_encoder = LabelEncoder()
    y_encoded = label_encoder.fit_transform(y)
    
    # 3. Train/test split
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )
    print(f"\nSplit train/test: {len(X_train)} / {len(X_test)} échantillons")
    
    # 4. Create preprocessing pipeline
    preprocessor = create_preprocessing_pipeline()
    
    # 5. Train and evaluate models
    best_model, best_name, results = train_and_evaluate_models(
        X_train, X_test, y_train, y_test, preprocessor
    )
    
    # 6. Confusion matrix
    confusion_mat = generate_confusion_matrix(best_model, X_test, y_test)
    
    # 7. Feature importance
    feature_imp = get_feature_importance(best_model)
    
    # 8. Save everything
    save_model_and_metrics(best_model, best_name, results, confusion_mat, feature_imp)
    
    print("\n" + "=" * 60)
    print("   ENTRAINEMENT TERMINE AVEC SUCCES!")
    print("=" * 60)
    
    return best_model


if __name__ == "__main__":
    main()
