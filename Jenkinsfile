pipeline {
    agent any

    options {
        timestamps()
        disableConcurrentBuilds()
    }

    environment {
        IMAGE_NAME     = 'saad-fa23-bds-060-api'
        CONTAINER_NAME = 'fa23-bds-060-api'
        SENDER         = 'saad887504@gmail.com'
        INSTRUCTOR     = 'qasimalik@gmail.com'
        STUDENT_EMAIL  = 'saad887504@gmail.com'
    }

    stages {
        stage('Checkout') {
            steps {
                checkout scm
                script {
                    env.GIT_COMMIT = sh(script: 'git rev-parse HEAD', returnStdout: true).trim()
                    env.COMMITTER_EMAIL = sh(script: 'git log -1 --pretty=format:%ae', returnStdout: true).trim()
                    env.COMMITTER_NAME = sh(script: 'git log -1 --pretty=format:%an', returnStdout: true).trim()
                    env.COMMIT_MSG = sh(script: 'git log -1 --pretty=format:%s', returnStdout: true).trim()
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

        stage('Push to DockerHub') {
            steps {
                withCredentials([usernamePassword(
                    credentialsId: 'dockerhub-creds',
                    usernameVariable: 'DH_USER',
                    passwordVariable: 'DH_PASS'
                )]) {
                    sh '''
                        echo "$DH_PASS" | docker login -u "$DH_USER" --password-stdin
                        docker tag ${IMAGE_NAME}:${BUILD_NUMBER} $DH_USER/${IMAGE_NAME}:latest
                        docker push $DH_USER/${IMAGE_NAME}:latest
                        docker logout
                    '''
                    script {
                        env.HUB_IMAGE = "${DH_USER}/${IMAGE_NAME}:latest"
                    }
                }
            }
        }

        stage('Clean Old Images') {
            steps {
                sh '''
                    docker images ${IMAGE_NAME} --format '{{.Tag}}' \
                      | grep -v -x -e "${BUILD_NUMBER}" -e "latest" \
                      | xargs -r -I{} docker rmi ${IMAGE_NAME}:{} || true
                    docker images fa23-bds-060-api -q | sort -u | xargs -r docker rmi -f || true
                    docker image prune -f || true
                '''
            }
        }
    }

    post {
        success {
            script { sendReport('SUCCESS') }
        }
        failure {
            script { sendReport('FAILED') }
        }
    }
}

def sendReport(String status) {
    def committer = env.COMMITTER_EMAIL ?: env.STUDENT_EMAIL
    def subject = "[FA23-BDS-060] Jenkins build #${env.BUILD_NUMBER} ${status}"
    def body = """Student Reg No: FA23-BDS-060
Job: ${env.JOB_NAME}
Build: #${env.BUILD_NUMBER}
Result: ${status}
Commit: ${env.GIT_COMMIT}
Committed by: ${env.COMMITTER_NAME} <${committer}>
Message: ${env.COMMIT_MSG}
DockerHub image: ${env.HUB_IMAGE}
Metrics: http://13.239.141.228:8000/metrics
Build URL: ${env.BUILD_URL}
"""
    // The committer always gets the report. The instructor is added only when
    // the commit was NOT made by the student (e.g. the grader pushing new data).
    def targets = []
    targets.add(env.INSTRUCTOR)
    if (!targets.contains(committer)) {
        targets.add(committer)
    }
    for (int i = 0; i < targets.size(); i++) {
        try {
            mail from: env.SENDER, to: targets[i], subject: subject, body: body
        } catch (e) {
            echo "Could not email ${targets[i]}: ${e}"
        }
    }
}