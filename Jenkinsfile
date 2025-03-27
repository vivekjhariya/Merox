pipeline {
    agent any
    stages {
        stage('Build') {
            steps {
                echo 'Building the Merox application...'
                sh 'docker --version' // Docker check
            }
        }
        stage('Test') {
            steps {
                echo 'Running tests...'
            }
        }
        stage('Deploy') {
            steps {
                echo 'Deploying the application...'
            }
        }
    }
}
