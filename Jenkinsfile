pipeline {
  agent {
    docker {
      image 'python:3.8'
    }

  }
  stages {
    stage('Message') {
      agent {
        docker {
          image 'python:3.8'
        }

      }
      steps {
        echo 'Hello World!'
      }
    }

  }
}