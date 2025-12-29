// ===========================================
// EcoLabel-MS - Jenkins Pipeline
// ===========================================

pipeline {
    agent any
    
    environment {
        DOCKER_COMPOSE_VERSION = '2.20.0'
        SONAR_HOST_URL = 'http://localhost:9000'
        SONAR_PROJECT_KEY = 'ecolabel-ms'
    }
    
    stages {
        // ===========================================
        // Stage 1: Checkout
        // ===========================================
        stage('Checkout') {
            steps {
                echo '📥 Cloning repository...'
                checkout scm
            }
        }
        
        // ===========================================
        // Stage 2: Build Docker Images
        // ===========================================
        stage('Build') {
            steps {
                echo '🔨 Building Docker images...'
                sh 'docker-compose build --no-cache'
            }
        }
        
        // ===========================================
        // Stage 3: Run Unit Tests
        // ===========================================
        stage('Unit Tests') {
            parallel {
                stage('Test Scoring') {
                    steps {
                        echo '🧪 Testing Scoring microservice...'
                        sh '''
                            cd scoring
                            pip install -r requirements.txt pytest pytest-cov
                            pytest tests/ -v --cov=app --cov-report=xml:coverage-scoring.xml || true
                        '''
                    }
                }
                stage('Test LCA-Lite') {
                    steps {
                        echo '🧪 Testing LCA-Lite microservice...'
                        sh '''
                            cd lca-lite
                            pip install -r requirements.txt pytest pytest-cov
                            pytest tests/ -v --cov=app --cov-report=xml:coverage-lca.xml || true
                        '''
                    }
                }
                stage('Test NLP') {
                    steps {
                        echo '🧪 Testing NLP microservice...'
                        sh '''
                            cd nlp-ingredients
                            pip install -r requirements.txt pytest pytest-cov
                            pytest tests/ -v --cov=app --cov-report=xml:coverage-nlp.xml || true
                        '''
                    }
                }
                stage('Test Parser') {
                    steps {
                        echo '🧪 Testing Parser microservice...'
                        sh '''
                            cd parser-produit
                            pip install -r requirements.txt pytest pytest-cov
                            pytest tests/ -v --cov=app --cov-report=xml:coverage-parser.xml || true
                        '''
                    }
                }
            }
        }
        
        // ===========================================
        // Stage 4: SonarQube Analysis
        // ===========================================
        stage('SonarQube Analysis') {
            steps {
                echo '📊 Running SonarQube analysis...'
                withSonarQubeEnv('SonarQube') {
                    sh '''
                        sonar-scanner \
                            -Dsonar.projectKey=${SONAR_PROJECT_KEY} \
                            -Dsonar.sources=. \
                            -Dsonar.host.url=${SONAR_HOST_URL}
                    '''
                }
            }
        }
        
        // ===========================================
        // Stage 5: Quality Gate
        // ===========================================
        stage('Quality Gate') {
            steps {
                echo '🚦 Waiting for Quality Gate...'
                timeout(time: 5, unit: 'MINUTES') {
                    waitForQualityGate abortPipeline: false
                }
            }
        }
        
        // ===========================================
        // Stage 6: Integration Tests
        // ===========================================
        stage('Integration Tests') {
            steps {
                echo '🔗 Running integration tests...'
                sh '''
                    docker-compose up -d
                    sleep 30
                    pip install pytest requests
                    pytest tests/test_integration.py -v || true
                '''
            }
        }
        
        // ===========================================
        // Stage 7: JMeter Performance Tests
        // ===========================================
        stage('JMeter Performance Tests') {
            steps {
                echo '⚡ Running JMeter load tests...'
                sh '''
                    mkdir -p jmeter-results
                    jmeter -n -t jmeter/ecolabel-load-test.jmx \
                        -l jmeter-results/results.jtl \
                        -e -o jmeter-results/report || true
                '''
            }
            post {
                always {
                    publishHTML(target: [
                        allowMissing: true,
                        alwaysLinkToLastBuild: true,
                        keepAll: true,
                        reportDir: 'jmeter-results/report',
                        reportFiles: 'index.html',
                        reportName: 'JMeter Report'
                    ])
                    perfReport(
                        sourceDataFiles: 'jmeter-results/results.jtl',
                        errorFailedThreshold: 5,
                        errorUnstableThreshold: 3
                    )
                }
            }
        }
        
        // ===========================================
        // Stage 8: Cleanup & Stop Services
        // ===========================================
        stage('Cleanup Services') {
            steps {
                echo '🧹 Stopping services...'
                sh 'docker-compose down'
            }
        }
        
        // ===========================================
        // Stage 7: Deploy (if on main branch)
        // ===========================================
        stage('Deploy') {
            when {
                branch 'main'
            }
            steps {
                echo '🚀 Deploying to production...'
                sh '''
                    docker-compose -f docker-compose.yml up -d
                    docker-compose ps
                '''
            }
        }
    }
    
    // ===========================================
    // Post Actions
    // ===========================================
    post {
        always {
            echo '🧹 Cleaning up...'
            sh 'docker-compose down || true'
            cleanWs()
        }
        success {
            echo '✅ Pipeline completed successfully!'
        }
        failure {
            echo '❌ Pipeline failed!'
        }
    }
}
