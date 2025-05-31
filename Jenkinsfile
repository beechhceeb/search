/* groovylint-disable CompileStatic, DuplicateStringLiteral, NestedBlockDepth, UnnecessaryGetter */
library 'mpb-toolbox'

// Do not build if triggered by a branch index
if (currentBuild.getBuildCauses().toString().contains('BranchIndexingCause')) {
    print 'INFO: Build skipped due to trigger being Branch Indexing'
    currentBuild.result = 'ABORTED'
    return
}

pipeline {
    agent {
        kubernetes {
            defaultContainer 'python'
            yamlFile 'ci-pod.yaml'
        }
    }

    environment {
        MPB_SKIP_UPDATES = '1'
        PYTHONPATH = './src'
        DEFAULT_BRANCH = 'main'
    }

    stages {
        stage ('NPM Setup') {
            steps {
                script {
                    sh '''
                        apt-get update
                        apt-get install -y curl gnupg
                        curl -fsSL https://deb.nodesource.com/setup_18.x | bash -
                        apt-get install -y nodejs
                        mkdir node_modules
                        npm ci
                    '''
                }
            }
        }
        stage('Setup Python') {
            environment {
                REQUIREMENTS = 'poetry.lock'
                POETRY_INSTALL_ARGS = '--no-interaction'
            }
            steps {
                sh './common/mpb setup'
            }
        }
        stage('Terraform Setup') {
            steps {
                script {
                    container('terraform') {
                        dir("devops/albatross/terraform/stages/10-main") {
                            gitUtils.withCreds({
                                sh "terraform init"
                            })
                        }
                    }
                }
            }
        }

        stage('Test') {
            parallel {
                stage('Lint') {
                    steps {
                        sh './common/mpb lint-python'
                    }
                }
                stage('Type Check') {
                    steps {
                        sh './common/mpb build-scripts/python'
                    }
                }
                stage('Tests and SonarQube') {
                    steps {
                        script {
                            sh './common/mpb test'
                        }
                    }
                }
            }
        }

        stage('Coverage') {
            steps {
                sh 'mv .coverage .coverage-tests'
                sh './env/bin/coverage combine .coverage-tests'
                sh './common/mpb coverage'
                publishHTML target: [
                    reportName: 'Coverage Report',
                    reportDir: './htmlcov',
                    reportFiles: 'index.html',
                    keepAll: true,
                    alwaysLinkToLastBuild: true,
                ]
            }
        }

        stage('Tag Release') {
            when {
                branch 'main'
            }
            steps {
                script {
                    deployment.tagRelease()
                }
            }
        }

        stage('Build albatross') {
            when {
                branch 'main'
            }
            steps {
                script {
                    def version = deployment.getVersionNumber()

                    def config = deployment.createDockerBuildConfig([
                        imageName: 'albatross',
                        version: version,
                        defaultBranchName: 'main',
                    ])

                    deployment.buildAndPublishDockerImage(
                        config
                    )
                }
            }
        }

        stage('Bootstrap') {
            when {
                branch 'main'
            }
            steps {
                build(
                    job: 'bootstrap-project',
                    wait: false,
                    parameters: [
                        string(name: 'TIER', value: 'albatross'),
                        string(name: 'SYSTEM', value: 'system'),
                    ]
                )
            }
        }

        stage('Deploy: 5-network') {
            when {
                branch 'main'
            }
            steps {
                container('terraform') {
                    script {
                        gitUtils.withCreds({
                            def version = deployment.getVersionNumber()
                            dir('devops/albatross/terraform/stages/5-network') {
                                sh 'terraform init -lock-timeout=600s'
                                sh "../../../../../common/mpb tf -e system -t albatross apply -lock-timeout=600s -auto-approve"
                            }
                        })
                    }
                }
            }
        }

        stage('Deploy: 10-main') {
            when {
                branch 'main'
            }
            steps {
                container('terraform') {
                    script {
                        gitUtils.withCreds({
                            def version = deployment.getVersionNumber()
                            dir('devops/albatross/terraform/stages/10-main') {
                                sh 'terraform init -lock-timeout=600s'
                                sh "../../../../../common/mpb tf -e system -t albatross apply -lock-timeout=600s -auto-approve -var albatross_version=${version}"
                            }
                        })
                    }
                }
            }
        }
    }
}