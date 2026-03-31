# GitHub Actions Runner Setup with Docker and Kubernetes

Setting up GitHub Actions Runner on your own servers using Docker and Kubernetes can greatly enhance your CI/CD workflows. This guide provides comprehensive steps to get you started.

## Prerequisites
1. **GitHub Account:** Ensure you have an active GitHub account.
2. **Docker:** Install Docker on your machine. Confirm installation with `docker --version`.
3. **Kubernetes Cluster:** Set up a Kubernetes cluster. You can use local tools like Minikube or a managed service like GKE, EKS, or AKS.

## Step 1: Create a Personal Access Token
1. Go to your GitHub account settings.
2. Navigate to **Developer settings** > **Personal access tokens** > **Tokens (classic)**.
3. Click on **Generate new token** and set the required scopes, e.g., `repo`, `workflow`.
4. Copy the generated token; you will need it later.

## Step 2: Set Up the Docker File
Create a `Dockerfile` for the GitHub Actions Runner:
```dockerfile
FROM ubuntu:20.04

RUN apt-get update && \
    apt-get install -y curl && \
    curl -o actions-runner-linux-x64.tar.gz -L https://github.com/actions/runner/releases/latest/download/actions-runner-linux-x64-2.281.0.tar.gz && \
    tar xzf ./actions-runner-linux-x64.tar.gz && \
    ./bin/installdependencies.sh

WORKDIR /actions-runner
ENTRYPOINT ["./run.sh"]
```

## Step 3: Create a Kubernetes Deployment
Create a Kubernetes manifest file (e.g., `k8s-deployment.yaml`):
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: github-actions-runner
spec:
  replicas: 1
  selector:
    matchLabels:
      app: github-actions-runner
  template:
    metadata:
      labels:
        app: github-actions-runner
    spec:
      containers:
      - name: runner
        image: your_docker_image:latest
        env:
          - name: RUNNER_TOKEN
            value: your_personal_access_token
        volumeMounts:
          - name: runner-data
            mountPath: /actions-runner
      volumes:
        - name: runner-data
          emptyDir: {}
```

## Step 4: Deploy to Kubernetes
Run the following command to deploy the runner:
```bash
kubectl apply -f k8s-deployment.yaml
```

## Step 5: Verify the Setup
To verify if the runner is active, go to your repository on GitHub:
1. Navigate to **Settings** > **Actions** > **Runners**.
2. You should see your runner listed and available for workflows.

## Conclusion
You now have a GitHub Actions Runner set up using Docker and Kubernetes! This setup allows you to run workflows directly in your environment, providing flexibility and control over your CI/CD pipelines.