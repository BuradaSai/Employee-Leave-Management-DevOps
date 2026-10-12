
pipeline {
    agent any

    options {
        timestamps()
    }

    environment {
        IMAGE_NAME = 'employee-leave-management'
        CONTAINER_NAME = 'employee-leave-container'
        APP_PORT = '5001'
    }

    stages {
        stage('Checkout') {
            steps {
                checkout scm
            }
        }

        
stage('Install Dependencies') {
    steps {
        bat '"C:/Users/saibu/AppData/Local/Programs/Python/Python312/python.exe" -m venv .venv'
        bat '.venv/Scripts/python.exe -m pip install -r requirements.txt'
    }
}


        stage('Unit Tests') {
            steps {
               
bat '''
    set APP_URL=http://127.0.0.1:5001
    .venv/Scripts/python.exe -m pytest tests/test_selenium.py -v
'''

            }
        }

        stage('Build Docker Image') {
            steps {
                bat 'docker build -t %IMAGE_NAME% .'
            }
        }

        stage('Deploy Container') {
            steps {
                bat '''
                    docker rm -f %CONTAINER_NAME% 2>NUL
                    docker run -d --name %CONTAINER_NAME% -p %APP_PORT%:5000 %IMAGE_NAME%
                '''
            }
        }

        stage('Wait for Application') {
            steps {
                powershell '''
                    $ready = $false
                    for ($i = 0; $i -lt 30; $i++) {
                        try {
                            $response = Invoke-WebRequest `
                                -Uri "http://127.0.0.1:5001/" `
                                -UseBasicParsing `
                                -TimeoutSec 2
                            if ($response.StatusCode -eq 200 -or
                                $response.StatusCode -eq 302) {
                                $ready = $true
                                break
                            }
                        } catch {}
                        Start-Sleep -Seconds 2
                    }
                    if (-not $ready) {
                        docker logs employee-leave-container
                        throw "Application did not become ready"
                    }
                '''
            }
        }

        stage('Selenium Tests') {
            steps {
                bat '''
                    set APP_URL=http://127.0.0.1:5001
                    python -m pytest tests/test_selenium.py -v
                '''
            }
        }
    }

    post {
        success {
            echo 'SUCCESS: Tests passed and Docker deployment completed.'
        }
        failure {
            echo 'FAILED: Check the stage logs to identify the problem.'
        }
    }
}
