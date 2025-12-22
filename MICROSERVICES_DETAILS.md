# Documentation Détaillée des Microservices EcoLabel

Ce document décrit en détail le fonctionnement, le rôle, la configuration technique et les mécanismes de communication de chaque microservice de l'architecture EcoLabel.

---

## Vue d'Ensemble des Communications

L'architecture repose sur des **appels HTTP synchrones (REST)** pour le déclenchement des actions et un modèle de **Base de Données Partagée** (Shared Database Pattern) pour la persistance des résultats intermédiaires.

*   **Protocole** : HTTP/1.1 (REST API).
*   **Format d'échange** : JSON.
*   **Base de Données** : PostgreSQL (Port `5432` - Service `postgres`). Chaque service a ses tables, mais tous partagent l'instance.
*   **Stockage de Fichiers** : MinIO (Port `9000` - Service `minio`). Compatible S3 pour stocker les rapports et fichiers bruts.

---

## 1. Service : ParserProduit (`parser-produit`)

### 📋 Fiche Technique
*   **Port** : `8001`
*   **Conteneur Docker** : `parser-produit`
*   **Image** : `parser-produit:latest`
*   **Dépendances** : `postgres`

### 🎯 Rôle
C'est la porte d'entrée des données brutes. Il transforme des formats non structurés (images, PDF, HTML) en texte exploitable par la machine.

### ⚙️ Fonctionnement Interne
1.  **Réception** : Reçoit un fichier via l'endpoint `/product/parse`.
2.  **Traitement** :
    *   **Images** : Utilise **Tesseract OCR** (via `pytesseract`) pour lire le texte sur les pixels.
    *   **HTML** : Utilise **BeautifulSoup** pour nettoyer les balises et garder le contenu textuel.
3.  **Encodage** : Convertit le tout en chaîne de caractères UTF-8.
4.  **Persistance** : Sauvegarde le texte brut et les métadonnées (GTIN, source) dans la table `product_raw`.

### 📡 Communication
*   **Entrée** : POST `http://localhost:8001/product/parse` (Multipart Form Data).
*   **Sortie** : JSON contenant le texte extrait + ID d'enregistrement en base.

---

## 2. Service : NLPIngrédients (`nlp-ingredients`)

### 📋 Fiche Technique
*   **Port** : `8002`
*   **Conteneur Docker** : `nlp-ingredients`
*   **Image** : `nlp-ingredients:latest`
*   **Dépendances** : `postgres`

### 🎯 Rôle
Le "cerveau" sémantique. Il lit le texte brut pour comprendre de quoi est composé le produit.

### ⚙️ Fonctionnement Interne
1.  **Réception** : Reçoit un bloc de texte brut.
2.  **Analyse (IA)** : Utilise un modèle **Transformer (BERT)** multilingue (via Hugging Face) pour effectuer la **reconnaissance d'entités nommées (NER)**.
    *   Il détecte les mots clés qui ressemblent à des ingrédients (ex: "Tomate", "Sucre").
    *   Il détecte les lieux (ex: "France", "Espagne") pour l'origine.
3.  **Normalisation** : Nettoie les noms (ex: "Tomates fraîches" -> "tomcat").
4.  **Persistance** : Sauvegarde les entités extraites dans `extraction_log`.

### 📡 Communication
*   **Entrée** : POST `http://localhost:8002/nlp/extract` (JSON avec texte brut).
*   **Sortie** : JSON avec liste structurée des ingrédients et lieux.

---

## 3. Service : LCALite (`lca-lite`)

### 📋 Fiche Technique
*   **Port** : `8003`
*   **Conteneur Docker** : `lca-lite`
*   **Image** : `lca-lite:latest`
*   **Dépendances** : `postgres`, `minio`

### 🎯 Rôle
Le calculateur scientifique. Il traduit les ingrédients en impacts environnementaux (Analyse du Cycle de Vie).

### ⚙️ Fonctionnement Interne
1.  **Réception** : Reçoit une liste structurée d'ingrédients et d'emballages.
2.  **Mapping** : Cherche dans sa table `emission_factors` les facteurs correspondants (ex: 1kg Tomate = 0.4kg CO2).
3.  **Calcul (Pandas)** :
    *   Somme le CO2, l'Eau et l'Énergie pour chaque composant.
    *   Ajoute une estimation pour le transport et l'emballage.
4.  **Génération de Rapport** : Crée un fichier CSV détaillé stocké sur **MinIO** (Bucket `lca-reports`).
5.  **Persistance** : Sauvegarde les totaux (indicateurs) dans `lca_results`.

### 📡 Communication
*   **Entrée** : POST `http://localhost:8003/lca/calc` (JSON).
*   **Sortie** : JSON avec les 3 indicateurs clés (CO2, Eau, Énergie).

---

## 4. Service : Scoring (`scoring`)

### 📋 Fiche Technique
*   **Port** : `8004`
*   **Conteneur Docker** : `scoring`
*   **Image** : `scoring:latest`
*   **Dépendances** : `postgres`

### 🎯 Rôle
Le juge. Il transforme des indicateurs techniques complexes en une note simple pour le consommateur.

### ⚙️ Fonctionnement Interne
1.  **Réception** : Reçoit les totaux d'impact (CO2, Eau, Énergie).
2.  **Normalisation** : Compare ces valeurs à des références (produit moyen vs produit polluant).
3.  **Pondération (Scikit-learn)** : Applique une formule (ex: 50% Importance Carbone, 25% Eau, 25% Énergie).
4.  **Classement** : Convertit le score numérique (0-100) en lettre (A, B, C, D, E).
5.  **Persistance** : Enregistre le score final dans `product_scores`.

### 📡 Communication
*   **Entrée** : POST `http://localhost:8004/score/compute` (JSON avec indicateurs).
*   **Sortie** : JSON avec Score Numérique, Lettre et Indice de confiance.

---

## 5. Service : WidgetAPI & UI (`widget-api` / `widget-ui`)

### 📋 Fiche Technique (Backend)
*   **Port** : `8005`
*   **Conteneur** : `widget-api`
*   **Dépendances** : `postgres`, `scoring`

### 📋 Fiche Technique (Frontend)
*   **Port** : `3000`
*   **Conteneur** : `widget-ui`
*   **URL Accès** : `http://localhost:3000`

### 🎯 Rôle
La vitrine. Permet aux utilisateurs finaux de visualiser les scores.

### ⚙️ Fonctionnement Interne
*   **Backend (FastAPI)** : Agit comme une couche de lecture seule. Il interroge la table `product_scores` pour récupérer les derniers calculs sans refaire tout le traitement.
*   **Frontend (React)** : Interface utilisateur moderne qui interroge le backend pour afficher les résultats en temps réel avec un code couleur dynamique.

### 📡 Communication
*   **API Public** : GET `http://localhost:8005/public/product/{name}`.

---

## 6. Service : Provenance (`provenance`)

### 📋 Fiche Technique
*   **Port** : `8006`
*   **Conteneur Docker** : `provenance`
*   **Image** : `provenance:latest`
*   **Dépendances** : `minio`

### 🎯 Rôle
L'auditeur (Boîte noire). Assure la traçabilité et la reproductibilité scientifique.

### ⚙️ Fonctionnement Interne
1.  **Réception** : Reçoit des métadonnées après chaque calcul de score.
2.  **Versioning (MLflow/DVC)** :
    *   Note quelle version du modèle de calcul a été utilisée (ex: v1.2).
    *   Note quel jeu de données de facteurs d'émission était actif (via Hash DVC).
3.  **Archivage** : Stocke ce "snapshot" pour qu'on puisse prouver plus tard pourquoi un produit a reçu la note A.

### 📡 Communication
*   **Entrée** : POST `http://localhost:8006/provenance/log`.
*   **Sortie** : JSON (Détails d'audit).
