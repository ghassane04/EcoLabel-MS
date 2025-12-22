# 4. Conception de Chaque Microservice

Voici les diagrammes UML (Classes et Cas d'Utilisation) générés en syntaxe **PlantUML** pour chaque microservice.

---

## 4.1 Microservice ParserProduit

### 4.1.1 Diagramme de classes – ParserProduit

```plantuml
@startuml
class ProductRaw {
  +id : Integer
  +gtin : String
  +raw_text : Text
  +source_type : String
  +created_at : DateTime
}

class ParserController {
  +parse_product(file: UploadFile) : JSON
}

class OCRService {
  +extract_text_from_image(image: bytes) : String
  +extract_text_from_html(html: String) : String
}

ParserController --> OCRService : uses
ParserController --> ProductRaw : creates
@enduml
```

### 4.1.2 Cas d’utilisation – ParserProduit

```plantuml
@startuml
left to right direction
actor "Système Externe / Utilisateur" as User

package ParserProduit {
  usecase "Uploader Fichier (Image/PDF)" as UC1
  usecase "Extraire Texte Brut (OCR)" as UC2
  usecase "Sauvegarder Données Brutes" as UC3
}

User --> UC1
UC1 ..> UC2 : include
UC2 ..> UC3 : include
@enduml
```

---

## 4.2 Microservice NLPIngrédients

### 4.2.1 Diagramme de classes – NLPIngrédients

```plantuml
@startuml
class ExtractionLog {
  +id : Integer
  +raw_text_hash : String
  +extracted_data : JSON
  +created_at : DateTime
}

class IngredientTaxonomy {
  +id : Integer
  +name : String
  +impact_factor_id : Integer
}

class NLPController {
  +extract_entities(request: ExtractionRequest) : JSON
}

class NERModel {
  +predict(text: String) : List<Entity>
}

NLPController --> NERModel : uses
NLPController --> ExtractionLog : logs
NLPController ..> IngredientTaxonomy : references
@enduml
```

### 4.2.2 Cas d’utilisation – NLPIngrédients

```plantuml
@startuml
left to right direction
actor "ParserProduit" as Parser

package NLPIngrédients {
  usecase "Recevoir Texte Brut" as UC1
  usecase "Identifier Ingrédients (NER)" as UC2
  usecase "Identifier Lieux d'Origine" as UC3
  usecase "Normaliser Noms d'Ingrédients" as UC4
}

Parser --> UC1
UC1 ..> UC2 : include
UC1 ..> UC3 : include
UC2 ..> UC4 : include
@enduml
```

---

## 4.3 Microservice LCALite

### 4.3.1 Diagramme de classes – LCALite

```plantuml
@startuml
class LCAResult {
  +id : Integer
  +product_ref : String
  +total_co2_kg : Float
  +total_water_l : Float
  +total_energy_mj : Float
  +report_url : String
}

class EmissionFactor {
  +id : Integer
  +name : String
  +category : String
  +co2_factor : Float
  +water_factor : Float
  +energy_factor : Float
}

class LCAController {
  +calculate_impact(ingredients: List) : LCAResult
}

class ReportGenerator {
  +generate_csv(data: Dict) : File
  +upload_to_minio(file: File) : String
}

LCAController --> EmissionFactor : queries
LCAController --> LCAResult : creates
LCAController --> ReportGenerator : uses
@enduml
```

### 4.3.2 Cas d’utilisation – LCALite

```plantuml
@startuml
left to right direction
actor "NLPIngrédients" as NLP

package LCALite {
  usecase "Recevoir Liste Ingrédients" as UC1
  usecase "Récupérer Facteurs Émission" as UC2
  usecase "Calculer Impacts (CO2, H2O, Énergie)" as UC3
  usecase "Générer Rapport CSV" as UC4
  usecase "Stocker Rapport sur MinIO" as UC5
}

NLP --> UC1
UC1 ..> UC2 : include
UC2 ..> UC3 : include
UC3 ..> UC4 : include
UC4 ..> UC5 : include
@enduml
```

---

## 4.4 Microservice Scoring

### 4.4.1 Diagramme de classes – Scoring

```plantuml
@startuml
class ProductScore {
  +id : Integer
  +product_name : String
  +score_numerical : Float
  +score_letter : Char
  +confidence_level : Float
  +version : String
}

class ScoreController {
  +compute_score(indicators: ScoreRequest) : ScoreResponse
}

class ScoringAlgorithm {
  +normalize(value: Float, ref: Float) : Float
  +weighted_sum(co2: Float, water: Float, energy: Float) : Float
  +get_letter_grade(score: Float) : Char
}

ScoreController --> ScoringAlgorithm : uses
ScoreController --> ProductScore : persists
@enduml
```

### 4.4.2 Cas d’utilisation – Scoring

```plantuml
@startuml
left to right direction
actor "LCALite" as LCA

package ScoringService {
  usecase "Recevoir Indicateurs ACV" as UC1
  usecase "Normaliser Valeurs" as UC2
  usecase "Calculer Score Pondéré" as UC3
  usecase "Attribuer Lettre (A-E)" as UC4
  usecase "Stocker Score Final" as UC5
}

LCA --> UC1
UC1 ..> UC2 : include
UC2 ..> UC3 : include
UC3 ..> UC4 : include
UC4 ..> UC5 : include
@enduml
```

---

## 4.5 Microservice WidgetAPI / Widget UI

### 4.5.1 Diagramme de classes – WidgetAPI / UI

```plantuml
@startuml
package "Backend (API)" {
  class ProductScoreReadModel {
    +product_name : String
    +score_letter : String
    +created_at : DateTime
  }
  class WidgetController {
    +get_product(name: String) : JSON
    +list_products() : List
  }
}

package "Frontend (React)" {
  class App {
    +state : products
    +handleSearch()
  }
  class ProductCard {
    +displayScore()
  }
}

WidgetController ..> ProductScoreReadModel : uses
App --> WidgetController : HTTP GET
App *-- ProductCard
@enduml
```

### 4.5.2 Cas d’utilisation – WidgetAPI / UI

```plantuml
@startuml
left to right direction
actor "Consommateur" as User

package WidgetSystem {
  usecase "Rechercher Produit par Nom" as UC1
  usecase "Visualiser Éco-Score (Couleur/Lettre)" as UC2
  usecase "Consulter Détails Impact" as UC3
  usecase "Voir Historique Recherches" as UC4
}

User --> UC1
User --> UC4
UC1 ..> UC2 : include
UC2 <.. UC3 : extend
@enduml
```

---

## 4.6 Microservice Provenance

### 4.6.1 Diagramme de classes – Provenance

```plantuml
@startuml
class ProvenanceRecord {
  +score_id : Integer
  +calculation_date : DateTime
  +model_version : String
  +dataset_hash : String
  +parameters : JSON
}

class ProvenanceController {
  +log_provenance(record: ProvenanceRecord)
  +get_audit(score_id: Integer)
}

class MLflowClient {
  +log_param(key: String, value: String)
  +start_run(run_name: String)
}

ProvenanceController --> MLflowClient : uses
@enduml
```

### 4.6.2 Cas d’utilisation – Provenance

```plantuml
@startuml
left to right direction
actor "Scoring Service" as Scoring
actor "Auditeur" as Auditor

package ProvenanceService {
  usecase "Enregistrer Contexte Calcul (Log)" as UC1
  usecase "Versionner Modèle & Données" as UC2
  usecase "Consulter Audit Score" as UC3
}

Scoring --> UC1
UC1 ..> UC2 : include
Auditor --> UC3
@enduml
```
