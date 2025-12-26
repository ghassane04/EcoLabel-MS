"""
Script to generate confusion matrix for the Scoring ML model
Saves the confusion matrix as PNG for report
"""

import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import confusion_matrix, classification_report, accuracy_score
import matplotlib.pyplot as plt
import seaborn as sns
import os

# Paths
DATA_PATH = 'data/training_dataset.csv'
OUTPUT_PATH = 'confusion_matrix.png'

def generate_confusion_matrix():
    print("=" * 60)
    print("Generating Confusion Matrix for EcoLabel Scoring")
    print("=" * 60)
    
    # Load data
    df = pd.read_csv(DATA_PATH)
    print(f"\n📊 Dataset loaded: {len(df)} samples")
    
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
    
    # Distribution
    unique, counts = np.unique(y, return_counts=True)
    print(f"\n📈 Class distribution:")
    for label, count in zip(unique, counts):
        print(f"   {label}: {count} samples ({count/len(y)*100:.1f}%)")
    
    # Split data
    X_train, X_test, y_train, y_test = train_test_split(
        X, y_encoded, test_size=0.2, random_state=42, stratify=y_encoded
    )
    
    print(f"\n🔄 Train: {len(X_train)} | Test: {len(X_test)}")
    
    # Train Random Forest
    print("\n🌲 Training Random Forest...")
    model = RandomForestClassifier(
        n_estimators=200,
        max_depth=15,
        min_samples_split=5,
        min_samples_leaf=2,
        class_weight='balanced',
        random_state=42,
        n_jobs=-1
    )
    model.fit(X_train, y_train)
    
    # Predictions
    y_pred = model.predict(X_test)
    
    # Metrics
    accuracy = accuracy_score(y_test, y_pred)
    print(f"\n✅ Accuracy: {accuracy:.2%}")
    
    # Classification report
    print("\n📋 Classification Report:")
    print(classification_report(y_test, y_pred, target_names=['A', 'B', 'C', 'D', 'E']))
    
    # Confusion Matrix
    cm = confusion_matrix(y_test, y_pred)
    
    # Plot
    plt.figure(figsize=(10, 8))
    
    # Create heatmap
    sns.heatmap(
        cm, 
        annot=True, 
        fmt='d', 
        cmap='Greens',
        xticklabels=['A', 'B', 'C', 'D', 'E'],
        yticklabels=['A', 'B', 'C', 'D', 'E'],
        cbar_kws={'label': 'Nombre de prédictions'}
    )
    
    plt.title(f'Matrice de Confusion - Scoring EcoLabel\n(Précision: {accuracy:.1%})', 
              fontsize=14, fontweight='bold')
    plt.xlabel('Classe Prédite', fontsize=12)
    plt.ylabel('Classe Réelle', fontsize=12)
    
    # Adjust layout
    plt.tight_layout()
    
    # Save
    plt.savefig(OUTPUT_PATH, dpi=300, bbox_inches='tight', facecolor='white')
    print(f"\n💾 Confusion matrix saved to: {OUTPUT_PATH}")
    
    # Also create a normalized version
    cm_normalized = cm.astype('float') / cm.sum(axis=1)[:, np.newaxis]
    
    plt.figure(figsize=(10, 8))
    sns.heatmap(
        cm_normalized, 
        annot=True, 
        fmt='.1%', 
        cmap='Blues',
        xticklabels=['A', 'B', 'C', 'D', 'E'],
        yticklabels=['A', 'B', 'C', 'D', 'E'],
        cbar_kws={'label': 'Pourcentage'}
    )
    
    plt.title(f'Matrice de Confusion Normalisée - Scoring EcoLabel\n(Précision: {accuracy:.1%})', 
              fontsize=14, fontweight='bold')
    plt.xlabel('Classe Prédite', fontsize=12)
    plt.ylabel('Classe Réelle', fontsize=12)
    
    plt.tight_layout()
    plt.savefig('confusion_matrix_normalized.png', dpi=300, bbox_inches='tight', facecolor='white')
    print(f"💾 Normalized confusion matrix saved to: confusion_matrix_normalized.png")
    
    print("\n" + "=" * 60)
    print("DONE!")
    print("=" * 60)
    
    return cm, accuracy


if __name__ == "__main__":
    generate_confusion_matrix()
