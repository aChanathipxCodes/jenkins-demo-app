pipeline {
  agent {
    docker {
      image 'docker:20.10.7'
      // ใช้ Docker-in-Docker ผ่าน docker.sock + ปิด entrypoint + โฟลเดอร์ config ที่เขียนได้
      args '--entrypoint="" -v /var/run/docker.sock:/var/run/docker.sock -e HOME=/var/jenkins_home -e DOCKER_CONFIG=/var/jenkins_home/.docker'
      reuseNode true
    }
  }

  options { skipDefaultCheckout(true) }
  environment { DOCKER_BUILDKIT = '1' }

  stages {
    stage('Checkout') {
      steps { checkout scm }
    }

    stage('Build Image') {
      steps {
        sh 'mkdir -p "$DOCKER_CONFIG"'
        // บังคับไม่ใช้ cache เผื่อแก้ requirements.txt
        sh 'docker build --pull --no-cache -t jenkins-demo-app:latest .'
      }
    }

    // ===== จุดเด่น: สแกนโค้ด app.py ด้วย Bandit แล้ว "ฟ้องว่า มีปัญหา" =====
    stage('SAST: Scan app.py') {
      steps {
        sh '''
          docker run --rm -v "$PWD":/src -w /src python:3.12-slim \
            sh -lc "pip install -q bandit && bandit -r app.py -f json -o .bandit.json || true"

          # ถ้าพบช่องโหว่ระดับ HIGH ให้ขึ้นข้อความ "มีปัญหา" แล้วทำให้สเตจล้ม
          if grep -q '"issue_severity": "HIGH"' .bandit.json; then
            echo "มีปัญหา: พบช่องโหว่ระดับ HIGH จาก Bandit ใน app.py"; exit 1;
          else
            echo "ปลอดภัยระดับ HIGH: ไม่พบบั๊กแรงใน app.py";
          fi
        '''
      }
    }

    // (ออปชัน) Smoke test ก่อน deploy: lib สำคัญต้อง import ได้
    stage('Smoke: imports') {
      steps {
        sh 'docker run --rm jenkins-demo-app:latest python -c "import flask, yaml; print(\'imports-ok\')"'
      }
    }

    stage('Deploy') {
      when { expression { return params.DEPLOY == null || params.DEPLOY == true } }
      steps {
        sh '''
          docker rm -f demo-app || true
          docker run -d --restart unless-stopped -p 5000:5000 --name demo-app jenkins-demo-app:latest

          # เช็คว่าขึ้นจริง และไม่มี Traceback
          sleep 2
          if docker logs demo-app 2>&1 | grep -Eqi "Traceback|ModuleNotFoundError"; then
            echo "มีปัญหา: แอปรันไม่ขึ้น ดู docker logs"; exit 1; fi

          curl -fsS http://localhost:5000/ >/dev/null || { echo "มีปัญหา: health check ล้มเหลว"; exit 1; }
        '''
      }
    }
  }

  post {
    always {
      archiveArtifacts allowEmptyArchive: true, artifacts: '.bandit.json'
      sh 'docker ps -a || true'
      sh 'docker logs demo-app | tail -n 80 || true'
    }
  }
}
