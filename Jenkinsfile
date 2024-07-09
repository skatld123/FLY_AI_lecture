pipeline {
    agent any
    parameters {
        choice(name: 'VERSION', choices: ['1.1.0', '1.2.0', '1.3.0'], description: '')
        booleanParam(name: 'executeTests', defaultValue: true, description: '')
    }
    stages {
        stage("init") {
            steps {
                script {
                    gv = load "script.groovy"
                }
            }
        }
        stage("Checkout") {
            steps {
                checkout scm
            }
        }
        stage('Verify Directory Structure') {
            steps {
                sh 'ls -alh'
                sh 'ls -alh MLOps_CICD/flaskapp'
            }
        }
        stage("Build") {
            steps {
                dir('MLOps_CICD/flaskapp') {
                    sh 'docker build -t flask-jenkins:v1.0.0 .'
                }
            }
        }
        stage("test") {
            when {
                expression {
                    params.executeTests
                }
            }
            steps {
                script {
                    gv.testApp()
                }
            }
        }
        stage("Tag and Push") {
            steps {
                withCredentials([[$class: 'UsernamePasswordMultiBinding',
                credentialsId: 'docker-hub',
                usernameVariable: 'DOCKER_USER_ID',
                passwordVariable: 'DOCKER_USER_PASSWORD'
                ]]) {
                    sh "docker tag flask-jenkins:v1.0.0 ${DOCKER_USER_ID}/jenkins-app:${BUILD_NUMBER}"
                    sh "docker login -u ${DOCKER_USER_ID} -p ${DOCKER_USER_PASSWORD}"
                    sh "docker push ${DOCKER_USER_ID}/jenkins-app:${BUILD_NUMBER}"
                }
            }
        }
        stage("deploy") {
            steps {
                echo 'deploying the application...'
            }
        }
    }
}
