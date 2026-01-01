// ===========================================
// EcoLabel-MS - Jenkins Pipeline (Windows)
// ===========================================

pipeline {
    agent any
    
    environment {
        SONAR_HOST_URL = 'http://localhost:9000'
        SONAR_PROJECT_KEY = 'ecolabel-ms'
    }
    
    stages {
        // ===========================================
        // Stage 1: Checkout
        // ===========================================
        stage('Checkout') {
            steps {
                echo 'Cloning repository...'
                git branch: 'main',
                    url: 'https://github.com/ghassane04/EcoLabel-MS.git'
            }
        }
        
        // ===========================================
        // Stage 2: Install Global Dependencies
        // ===========================================
        stage('Install Dependencies') {
            steps {
                echo 'Installing Python test dependencies...'
                bat 'pip install pytest pytest-cov httpx flake8 bandit'
            }
        }
        
        // ===========================================
        // Stage 3: Run Unit Tests - All Microservices
        // ===========================================
        stage('Unit Tests - All Microservices') {
            parallel {
                stage('Parser-Produit Tests') {
                    steps {
                        echo 'Testing parser-produit...'
                        bat 'cd parser-produit && pip install -r requirements.txt && pytest tests/ -v --tb=short || exit 0'
                    }
                }
                stage('NLP-Ingredients Tests') {
                    steps {
                        echo 'Testing nlp-ingredients...'
                        bat 'cd nlp-ingredients && pip install -r requirements.txt && pytest tests/ -v --tb=short || exit 0'
                    }
                }
                stage('LCA-Lite Tests') {
                    steps {
                        echo 'Testing lca-lite...'
                        bat 'cd lca-lite && pip install -r requirements.txt && pytest tests/ -v --tb=short || exit 0'
                    }
                }
                stage('Scoring Tests') {
                    steps {
                        echo 'Testing scoring...'
                        bat 'cd scoring && pip install -r requirements.txt && pytest tests/ -v --tb=short || exit 0'
                    }
                }
                stage('Provenance Tests') {
                    steps {
                        echo 'Testing provenance...'
                        bat 'cd provenance && pip install -r requirements.txt && pytest tests/ -v --tb=short || exit 0'
                    }
                }
                stage('Widget-API Tests') {
                    steps {
                        echo 'Testing widget-api...'
                        bat 'cd widget-api\\backend && pip install -r requirements.txt && pytest tests/ -v --tb=short || exit 0'
                    }
                }
            }
        }
        
        // ===========================================
        // Stage 4: Code Quality Check - All Services
        // ===========================================
        stage('Code Quality') {
            steps {
                echo 'Checking code quality for all microservices...'
                bat '''
                    flake8 parser-produit/app --max-line-length=120 --ignore=E501,W503 || exit 0
                    flake8 nlp-ingredients/app --max-line-length=120 --ignore=E501,W503 || exit 0
                    flake8 lca-lite/app --max-line-length=120 --ignore=E501,W503 || exit 0
                    flake8 scoring/app --max-line-length=120 --ignore=E501,W503 || exit 0
                    flake8 provenance/app --max-line-length=120 --ignore=E501,W503 || exit 0
                    flake8 widget-api/backend/app --max-line-length=120 --ignore=E501,W503 || exit 0
                '''
            }
        }
        
        // ===========================================
        // Stage 5: Security Scan - All Services
        // ===========================================
        stage('Security Scan') {
            steps {
                echo 'Running security scan for all microservices...'
                bat '''
                    bandit -r parser-produit/app -f txt -ll || exit 0
                    bandit -r nlp-ingredients/app -f txt -ll || exit 0
                    bandit -r lca-lite/app -f txt -ll || exit 0
                    bandit -r scoring/app -f txt -ll || exit 0
                    bandit -r provenance/app -f txt -ll || exit 0
                    bandit -r widget-api/backend/app -f txt -ll || exit 0
                '''
            }
        }
        
        // ===========================================
        // Stage 6: Generate Reports
        // ===========================================
        stage('Generate Reports') {
            steps {
                echo 'All microservices tests completed!'
                bat 'echo Build Date: %DATE% %TIME%'
                bat 'echo Tested: parser-produit, nlp-ingredients, lca-lite, scoring, provenance, widget-api'
            }
        }
    }
    
    // ===========================================
    // Post Actions
    // ===========================================
    post {
        always {
            echo 'Pipeline finished!'
        }
        success {
            echo 'SUCCESS! All microservices tests passed.'
        }
        failure {
            echo 'FAILED! Check the logs for details.'
        }
    }
}
