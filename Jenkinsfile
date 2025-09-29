pipeline {
  agent {
    docker {
      image 'docker:20.10.7'
      args '--entrypoint="" -v /var/run/docker.sock:/var/run/docker.sock -e HOME=/var/jenkins_home -e DOCKER_CONFIG=/var/jenkins_home/.docker'
      reuseNode true
    }
  }

  options { skipDefaultCheckout(true) }
  environment { DOCKER_BUILDKIT = '1' }

  stages {
    stage('Checkout') {
      steps {
        checkout scm
      }
    }

    stage('Build Image') {
      steps {
        sh 'mkdir -p "$DOCKER_CONFIG"'
        sh 'docker build -t jenkins-demo-app:latest .'
      }
    }

    stage('Test') {
      steps {
        sh 'docker run --rm -v "$PWD":/app -w /app jenkins-demo-app:latest sh -lc "pip install -q pytest || true; pytest -q || true"'
      }
    }

    stage('Deploy (Run Container)') {
      steps {
        sh 'docker rm -f demo-app || true'
        sh 'docker run -d --restart unless-stopped -p 5000:5000 --name demo-app jenkins-demo-app:latest'
      }
    }
  }

  post {
    always {
      sh 'docker ps -a || true'
      sh 'docker logs demo-app | tail -n 80 || true'
    }
  }
}
