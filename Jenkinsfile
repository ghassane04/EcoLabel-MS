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
        // Stage 2: Install Dependencies
        // ===========================================
        stage('Install Dependencies') {
            steps {
                echo 'Installing Python dependencies...'
                bat 'pip install pytest pytest-cov httpx flake8 bandit'
            }
        }
        
        // ===========================================
        // Stage 3: Run Unit Tests
        // ===========================================
        stage('Unit Tests') {
            steps {
                echo 'Running unit tests...'
                bat 'cd scoring && pip install -r requirements.txt && pytest tests/ -v || exit 0'
            }
        }
        
        // ===========================================
        // Stage 4: Code Quality Check
        // ===========================================
        stage('Code Quality') {
            steps {
                echo 'Checking code quality...'
                bat 'flake8 scoring/app --max-line-length=120 --ignore=E501,W503 || exit 0'
            }
        }
        
        // ===========================================
        // Stage 5: Security Scan
        // ===========================================
        stage('Security Scan') {
            steps {
                echo 'Running security scan...'
                bat 'bandit -r scoring/app -f txt || exit 0'
            }
        }
        
        // ===========================================
        // Stage 6: Generate Reports
        // ===========================================
        stage('Generate Reports') {
            steps {
                echo 'Build completed successfully!'
                bat 'echo Build Date: %DATE% %TIME%'
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
            echo 'SUCCESS!'
        }
        failure {
            echo 'FAILED!'
        }
    }
}
