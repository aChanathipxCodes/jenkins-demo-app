pipeline {
  agent {
    docker {
      image 'docker:20.10.7'
      args '--user 0:0 -v /var/run/docker.sock:/var/run/docker.sock'
    }
  }
  stages {
    stage('Checkout') {
      steps {
        git branch: 'main', url: 'https://github.com/aChanathipxCodes/jenkins-demo-app.git'
      }
    }
    stage('Build Image') {
      steps {
        sh 'docker build -t jenkins-demo-app:latest .'
      }
    }
    stage('Run Container') {
      steps {
        sh 'docker run -d -p 5000:5000 --name demo-app jenkins-demo-app:latest'
      }
    }
    stage('Test') {
      steps {
        sh 'echo "Running tests..."'
        sh 'pytest || true'
      }
    }
  }
}