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

    stage('Ansible') {
      agent any
      steps {
        sshagent(['ansible']) {
        sh 'ssh -o StrictHostKeyChecking=no ubuntu@192.168.55.105'
        sh 'scp -r /var/lib/jenkins/workspace/DevOps_main/* ubuntu@192.168.55.105:/home/ubuntu'
      }
      }

    }

    stage('Docker Build') {
      agent any
      steps {
        sshagent(['ansible']) {
        sh 'ssh -o StrictHostKeyChecking=no ubuntu@192.168.55.105 docker build app/. -t venkysvr/app'
        sh 'ssh -o StrictHostKeyChecking=no ubuntu@192.168.55.105 docker build web/. -t venkysvr/web'
      }
      }
    }
     stage('Docker push') {
      agent any
      steps {
        sshagent(['ansible']) {
          withCredentials([usernamePassword(credentialsId: 'docker', passwordVariable: 'docker_password', usernameVariable: 'docker_username')]) {
            sh 'ssh -o StrictHostKeyChecking=no ubuntu@192.168.55.105 docker login -u ${docker_username} -p ${docker_password}'
            sh 'ssh -o StrictHostKeyChecking=no ubuntu@192.168.55.105 docker push venkysvr/app'
        sh 'ssh -o StrictHostKeyChecking=no ubuntu@192.168.55.105 docker push venkysvr/web'
      
        }
        }
      }
    }

    stage('Kubernetes') {
      agent any
      steps {
        sshagent(['ansible']) {
        sh 'ssh -o StrictHostKeyChecking=no ubuntu@192.168.55.107'
        sh 'scp -r /var/lib/jenkins/workspace/DevOps_main/kubernetes/* ubuntu@192.168.55.107:/home/ubuntu'
      
      }
      }
    }

  }
}