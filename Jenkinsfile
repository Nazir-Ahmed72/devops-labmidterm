
pipeline {
    agent any

    options {
        timestamps()
        disableConcurrentBuilds()
    }

    environment {
        IMAGE_NAME = 'fa23-bds-060-api'
        CONTAINER_NAME = 'fa23-bds-060-api'
    }

    stages {
        stage('Checkout') {
            steps {
                checkout scm
                script {
                    env.GIT_COMMIT = sh(
                        script: 'git rev-parse HEAD',
                        returnStdout: true
                    ).trim()
                }
            }
        }

        stage('Train and Test') {
            steps {
                sh '''
                    docker run --rm \
                      -e GIT_COMMIT=${GIT_COMMIT} \
                      -v "$WORKSPACE:/app" \
                      -w /app \
                      python:3.11-slim \
                      bash -c "pip install -q -r requirements.txt pytest httpx && python train.py && python -m pytest -v"
                '''
            }
        }

        stage('Build Docker Image') {
            steps {
                sh '''
                    docker build -t ${IMAGE_NAME}:${BUILD_NUMBER} .
                    docker tag ${IMAGE_NAME}:${BUILD_NUMBER} ${IMAGE_NAME}:latest
                '''
            }
        }

        stage('Deploy') {
            steps {
                sh '''
                    docker rm -f ${CONTAINER_NAME} || true

                    docker run -d \
                      --name ${CONTAINER_NAME} \
                      --restart unless-stopped \
                      -p 8000:8000 \
                      ${IMAGE_NAME}:latest

                    sleep 5
                    curl -fsS http://127.0.0.1:8000/health
                    curl -fsS http://127.0.0.1:8000/metrics
                '''
            }
        }
    }

    post {
        success {
            echo 'Training, tests, Docker build and deployment successful!'
        }
        failure {
            echo 'Pipeline failed. Check Console Output.'
        }
    }
}
