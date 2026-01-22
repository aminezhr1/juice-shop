pipeline {
    agent any

    environment {
        NODE_ENV = 'development'
    }

    stages {
        stage('Checkout SCM') {
            steps {
                checkout scm
            }
        }

        stage('Install Dependencies') {
            steps {
                script {
                    // Retry npm install 3 times in case of network issues
                    retry(3) {
                        sh 'npm install --fetch-timeout=60000'
                    }
                }
            }
        }

        stage('Run Tests') {
            steps {
                sh 'npm test'
            }
        }

        stage('Run Juice Shop Server') {
            steps {
                script {
                    // Start Juice Shop in background
                    sh 'npm start &'
                    // Wait for server to start
                    sh 'sleep 10'
                }
            }
        }

        stage('DAST Scan with OWASP ZAP') {
            steps {
                script {
                    // Run OWASP ZAP baseline scan against local Juice Shop
                    sh '''
                    docker run --rm -t owasp/zap2docker-stable zap-baseline.py \
                    -t http://localhost:3000 \
                    -r zap_report.html
                    '''
                }
            }
        }
    }

    post {
        always {
            // Stop any background Juice Shop server
            sh "pkill -f 'node .*app.js' || true"

            // Archive the ZAP report
            archiveArtifacts artifacts: 'zap_report.html', allowEmptyArchive: true

            echo 'Pipeline finished.'
        }
        failure {
            echo 'Pipeline failed!'
        }
        success {
            echo 'Pipeline succeeded!'
        }
    }
}
