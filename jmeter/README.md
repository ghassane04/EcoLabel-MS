# ===========================================
# EcoLabel-MS - JMeter Tests
# ===========================================

## 📋 Description

Tests de performance et de charge pour les microservices EcoLabel-MS.

## 📁 Fichiers

| Fichier | Description |
|---------|-------------|
| `ecolabel-load-test.jmx` | Plan de test principal |
| `run-tests.sh` | Script d'exécution |
| `run-tests.bat` | Script Windows |

## 🚀 Exécution

### Prérequis

1. Télécharger JMeter : https://jmeter.apache.org/download_jmeter.cgi
2. Ajouter JMeter au PATH

### Lancer les tests

#### Mode GUI (pour le développement)
```bash
jmeter -t ecolabel-load-test.jmx
```

#### Mode CLI (pour CI/CD)
```bash
jmeter -n -t ecolabel-load-test.jmx -l results.jtl -e -o jmeter-report
```

### Options

| Option | Description |
|--------|-------------|
| `-n` | Mode non-GUI |
| `-t` | Fichier test plan |
| `-l` | Fichier résultats |
| `-e` | Générer dashboard |
| `-o` | Dossier rapport HTML |

## 📊 Scénarios de Test

### 1. Scoring API Load Test
- **Threads** : 10 utilisateurs simultanés
- **Loops** : 100 itérations
- **Ramp-up** : 10 secondes
- **Endpoints testés** :
  - `GET /health`
  - `POST /score/compute`

### 2. LCA API Load Test
- **Threads** : 5 utilisateurs
- **Loops** : 50 itérations
- **Ramp-up** : 5 secondes
- **Endpoints testés** :
  - `POST /lca/calc`

## 📈 Métriques Collectées

- Temps de réponse (min, max, avg)
- Throughput (requêtes/sec)
- Taux d'erreur
- Latence
- Percentiles (90th, 95th, 99th)

## 🎯 Critères de Performance

| Métrique | Objectif |
|----------|----------|
| Temps de réponse moyen | < 500ms |
| Throughput | > 50 req/s |
| Taux d'erreur | < 1% |
| 95th percentile | < 1s |

## 📂 Résultats

Les résultats sont sauvegardés dans :
- `jmeter-results/summary.csv` - Résumé CSV
- `jmeter-report/` - Dashboard HTML
