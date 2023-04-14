pipeline {
  agent any
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
        sh 'docker build api/. -t venkysvr/admin'
        sh 'docker build frontend/. -t venkysvr/client'
        sh 'docker build subprocess/. -t venkysvr/compiler'
      }
    }
     stage('Docker Hub') {
      agent any
      steps {
          withCredentials([usernamePassword(credentialsId: 'docker', passwordVariable: 'docker_password', usernameVariable: 'docker_username')]) {
            sh 'docker login -u ${docker_username} -p ${docker_password}'
            sh 'docker push venkysvr/admin'
            sh 'docker push venkysvr/client'
            sh 'docker push venkysvr/web'
        }
      }
    }

    stage('Kubernetes') {
      agent any
      steps {
        sh "sshpass -p ' ' scp -o StrictHostKeyChecking=no deploy.yaml ubuntu@192.168.55.102:/home/ubuntu"
        sh "sshpass -p ' ' ssh -o StrictHostKeyChecking=no ubuntu@192.168.55.102 'ls'"

      }
    }

  }
}