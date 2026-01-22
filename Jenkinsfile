pipeline {
    agent any
    environment {
        PATH = "/usr/bin:$PATH"
    }
    stages {
        stage('Install Dependencies') {
            steps {
                sh 'npm install'
            }
        }
        stage('Run Tests') {
            steps {
                sh 'npm test'
            }
        }
        stage('Run Juice Shop') {
            steps {
                sh 'npm start &'
                sh 'sleep 10'
            }
        }
        stage('DAST Scan with OWASP ZAP') {
            steps {
                sh 'docker run -t owasp/zap2docker-stable zap-baseline.py -t http://localhost:3000'
            }
        }
    }
}
