# 3. Architecture Détaillée des Microservices

## 3.2 Rôle de chaque microservice

*   **ParserProduit :**
    Ce microservice est responsable de l'acquisition et de la numérisation des données brutes. Son rôle principal est de transformer des documents non structurés (images de produits, étiquettes scannées, fichiers HTML ou PDF) en texte exploitable par la machine via des techniques d'OCR (Reconnaissance Optique de Caractères) et de parsing.

*   **NLPIngrédients :**
    Ce service agit comme le cerveau sémantique du système. Son rôle est d'analyser le texte brut extrait pour identifier, extraire et normaliser les entités clés nécessaires au calcul écologique, notamment la liste des ingrédients et les lieux d'origine, en utilisant des modèles d'Intelligence Artificielle (NER - Named Entity Recognition).

*   **LCALite :**
    Ce microservice est le moteur de calcul scientifique. Son rôle est d'effectuer l'Analyse du Cycle de Vie (ACV) simplifiée. Il mappe chaque ingrédient identifié à des facteurs d'émission (base de données Agribalyse simplifiée) pour calculer trois indicateurs d'impact environnemental : l'empreinte carbone (CO2), la consommation d'eau et la consommation d'énergie.

*   **Scoring :**
    Ce service est le système de notation final. Son rôle est d'agréger les indicateurs d'impact bruts (fournis par LCALite), de les normaliser par rapport à des valeurs de référence, et d'appliquer une pondération pour produire un « Écoscore » simple et compréhensible pour le consommateur (Note sur 100 et Classe A-E).

*   **WidgetAPI / Widget UI :**
    Ce duo de services constitue la couche de présentation.
    *   **WidgetAPI** : Expose les scores finaux via une API publique sécurisée pour les applications tierces.
    *   **Widget UI** : Fournit une interface graphique web (Dashboard) permettant aux consommateurs de rechercher un produit et de visualiser son score écologique sous forme de badges colorés.

*   **Provenance :**
    Ce service assure l'auditabilité et la reproductibilité scientifique. Son rôle est d'archiver les métadonnées de chaque calcul (version du modèle utilisée, hash du jeu de données, paramètres de pondération) pour garantir la traçabilité complète de la note attribuée.

---

## 3.3 Technologies utilisées par chaque microservice

| Microservice | Langage | Framework | Librairies Clés / Outils |
| :--- | :--- | :--- | :--- |
| **ParserProduit** | Python 3.11 | FastAPI | `pytesseract` (Tesseract OCR), `Pillow`, `BeautifulSoup4` |
| **NLPIngrédients** | Python 3.11 | FastAPI | `transformers` (Hugging Face BERT), `torch`, `pydantic` |
| **LCALite** | Python 3.11 | FastAPI | `pandas` (Calcul matriciel), `SQLAlchemy`, `MinIO SDK` |
| **Scoring** | Python 3.11 | FastAPI | `scikit-learn` (Normalisation), `numpy` |
| **WidgetAPI (Back)** | Python 3.11 | FastAPI | `SQLAlchemy`, `uvicorn` |
| **Widget UI (Front)** | JavaScript | React | `Vite`, `CSS3` (Glassmorphism), `Fetch API` |
| **Provenance** | Python 3.11 | FastAPI | `mlflow` (Tracking), `dvc` (Versioning), `git` |

---

## 3.4 Base de données associée à chaque microservice

| Microservice | Type de Stockage | Instance | Tables / Contenu |
| :--- | :--- | :--- | :--- |
| **ParserProduit** | SGBD Relationnel | PostgreSQL (`postgres`) | Table `product_raw` : Stocke le texte brut extrait et les métadonnées (GTIN). |
| **NLPIngrédients** | SGBD Relationnel | PostgreSQL (`postgres`) | Table `extraction_log` : Historique des extractions.<br>Table `ingredient_taxonomy` : Référentiel des ingrédients normalisés. |
| **LCALite** | SGBD + Object Storage | PostgreSQL (`postgres`)<br>MinIO (`minio`) | Table `emission_factors` : Facteurs d'émission (kgCO2/kg).<br>Table `lca_results` : Résultats agrégés.<br>**Bucket MinIO** `lca-reports` : Rapports CSV détaillés. |
| **Scoring** | SGBD Relationnel | PostgreSQL (`postgres`) | Table `product_scores` : Note finale, lettre (A-E), et niveau de confiance. |
| **WidgetAPI** | Lecture Seule | PostgreSQL (`postgres`) | Accès en lecture à la table `product_scores` pour afficher les résultats. |
| **Provenance** | Metastore + Object Storage | MinIO (`minio`)<br>Fichiers Locaux | Stocke les artefacts MLflow et les hash DVC des datasets. |

---

## 3.5 Méthodes de communication entre microservices

### 3.5.1 Type de communication
*   **Synchrone (REST HTTP)** : La majorité des échanges inter-services se fait via des appels API REST directs et synchrones. Lorsqu'un service a besoin d'une donnée traitée par un autre, il effectue une requête HTTP et attend la réponse (JSON).
*   **Persistance Partagée (Shared Database)** : Bien que chaque service ait sa logique, ils partagent la même instance PostgreSQL (mais avec des tables distinctes), ce qui permet une cohérence forte des données transactionnelles.

### 3.5.2 Outils et protocoles utilisés
*   **Protocole** : HTTP/1.1.
*   **Format de données** : JSON (application/json) pour les corps de requêtes et réponses.
*   **Découverte de services** : Résolution DNS interne de Docker (ex: appel via `http://parser-produit:8001`).
*   **Ports** : Chaque service écoute sur un port dédié (`8001` à `8006`).

### 3.5.3 Flux principaux entre microservices
1.  **Orchestration du Calcul** (Actuellement séquentiel via scripts ou API gateway simulée) :
    *   User -> **ParserProduit** (POST `/product/parse`): Envoi du fichier, retour de l'ID texte.
    *   User -> **NLPIngrédients** (POST `/nlp/extract`): Envoi du texte brut, retour des ingrédients.
    *   User -> **LCALite** (POST `/lca/calc`): Envoi des ingrédients, retour des indicateurs CO2/Eau.
2.  **Flux de Scoring** :
    *   User/Process -> **Scoring** (POST `/score/compute`): Envoi des indicateurs LCA, retour de la Note Finale.
3.  **Flux d'Audit (Parallèle)** :
    *   Scoring -> **Provenance** (POST `/provenance/log`): Envoi asynchrone (ou "fire and forget") des métadonnées du calcul pour archivage.
4.  **Flux de Consultation** :
    *   Browser -> **WidgetUI** (Port 3000).
    *   WidgetUI -> **WidgetAPI** (GET `/public/product/{name}`).
    *   WidgetAPI -> **PostgreSQL** (SELECT sur `product_scores`).
