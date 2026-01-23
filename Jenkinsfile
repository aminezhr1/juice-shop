pipeline {
    agent any

    environment {
        NODE_ENV   = 'development'
        TARGET_URL = 'http://localhost:3000'
        JAVA_PROJECT_DIR = './'  // adjust if you have a Java project for SpotBugs
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
                    retry(3) {
                        sh '''
                        echo "[+] Installing Node dependencies"
                        npm ci --fetch-timeout=60000
                        '''
                    }
                }
            }
        }

        stage('Run Tests') {
            steps {
                sh 'npm test || true'
            }
        }

        stage('Start Juice Shop') {
            steps {
                script {
                    sh '''
                    echo "[+] Starting Juice Shop"
                    nohup npm start > juice-shop.log 2>&1 &

                    echo "[+] Waiting for Juice Shop to be ready..."
                    for i in {1..30}; do
                        if curl -s $TARGET_URL > /dev/null; then
                            echo "[✓] Juice Shop is up"
                            break
                        fi
                        sleep 5
                    done
                    '''
                }
            }
        }

        stage('Run Security Scans (Python)') {
            steps {
                script {
                    sh '''
                    echo "[+] Running security_scan.py"
                    python3 security_scan.py
                    '''
                }
            }
        }

        stage('Generate High-Risk Report') {
            steps {
                script {
                    sh '''
                    echo "[+] Generating high-risk report"
                    python3 high_risk_report.py
                    '''
                }
            }
        }

        stage('DAST Scan with OWASP ZAP (Docker)') {
            steps {
                script {
                    sh '''
                    echo "[+] Running OWASP ZAP baseline scan (Docker)"
                    docker run --rm -t --network="host" \
                        -v $(pwd):/zap/wrk \
                        owasp/zap2docker-stable zap-baseline.py \
                        -t $TARGET_URL \
                        -r zap_report.html
                    '''
                }
            }
        }
    }

    post {
        always {
            echo "[+] Cleaning up Juice Shop process"
            sh "pkill -f 'node .*app.js' || true"

            echo "[+] Archiving all reports"
            archiveArtifacts artifacts: '''
                reports/**
                zap_report.html
                juice-shop.log
            ''', allowEmptyArchive: true

            echo 'Pipeline finished.'
        }

        failure {
            echo '❌ Pipeline failed'
        }

        success {
            echo '✅ Pipeline succeeded'
        }
    }
}
