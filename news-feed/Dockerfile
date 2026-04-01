name: CI - Build, Scan, Push (Podman)

on:
  push:
    branches: [ main ]
  pull_request:

jobs:
  build-and-push:
    runs-on: ubuntu-latest
    env:
      IMAGE_NAME: yourdockerhubusername/news-feed:latest

    steps:
    - name: Checkout code
      uses: actions/checkout@v3

    - name: Set up JDK 17
      uses: actions/setup-java@v3
      with:
        java-version: '17'
        distribution: 'temurin'

    - name: Build Maven project
      run: mvn clean package -DskipTests

    - name: Install Podman
      run: |
        sudo apt-get update
        sudo apt-get install -y podman

    - name: Log in to Docker Hub with Podman
      run: |
        echo "${{ secrets.DOCKER_PASSWORD }}" | podman login docker.io \
          --username ${{ secrets.DOCKER_USERNAME }} --password-stdin

    - name: Build Docker image with Podman
      run: podman build -t $IMAGE_NAME .

    - name: Scan image with Trivy
      run: trivy image --exit-code 1 $IMAGE_NAME

    - name: Push image to Docker Hub
      run: podman push $IMAGE_NAME