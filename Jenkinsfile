pipeline {
  agent any

   environment {
    admin_version = "v0.1"
    client_version = "v0.1"
    compiler_version = "v0.1"
  }


  stages {
    stage('Git') {
      agent any
      steps {
        sh 'pwd'
        sh 'ls'
      }
    }

    stage('Docker Build') {
      agent any
      steps {
        sh 'docker build api/. -t venkysvr/admin:${admin_version}'
        sh 'docker build frontend/. -t venkysvr/client:${client_version}'
        sh 'docker build subprocess/. -t venkysvr/compiler:${compiler_version}'
      }
    }
     stage('Docker Hub') {
      agent any
      steps {
          withCredentials([usernamePassword(credentialsId: 'docker', passwordVariable: 'docker_password', usernameVariable: 'docker_username')]) {
            sh 'docker login -u ${docker_username} -p ${docker_password}'
            sh 'docker push venkysvr/admin:${admin_version}'
            sh 'docker push venkysvr/client:${client_version}'
            sh 'docker push venkysvr/compiler:${compiler_version}'
        }
      }
    }

    stage('Unit Test') {
      agent any
      steps {
        sh 'cd subprocess'
        sh 'pwd'
        sh 'pip install Flask'
        sh 'python3 subprocess/test_app.py'
      }
    }


    stage('Kubernetes') {
      agent any
      steps {
        sh 'cd ../'
        sh 'pwd'
        sh "sshpass -p ' ' scp -o StrictHostKeyChecking=no deploy.yaml ubuntu@192.168.55.102:/home/ubuntu"
        sh "sshpass -p ' ' ssh -o StrictHostKeyChecking=no ubuntu@192.168.55.102 'microk8s.kubectl apply -f deploy.yaml'"

      }
    }

  }
}