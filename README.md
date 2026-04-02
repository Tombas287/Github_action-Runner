# GitHub Actions Runner with Kubernetes & Spring Boot News Feed

A production-ready GitHub Actions Runner setup containerized with Docker and deployed on Kubernetes, integrated with a Spring Boot News Feed microservice application for CI/CD demonstrations.

**Table of Contents**
- [Project Overview](#project-overview)
- [Architecture](#architecture)
- [Components](#components)
- [Prerequisites](#prerequisites)
- [Implementation Steps](#implementation-steps)
- [Deployment Guide](#deployment-guide)
- [Configuration](#configuration)
- [Troubleshooting](#troubleshooting)

## Project Overview

This project demonstrates a complete CI/CD pipeline infrastructure consisting of:
- **GitHub Actions Runner**: Scalable, containerized CI/CD runner deployed on Kubernetes
- **News Feed Application**: Spring Boot microservice that fetches news from multiple categories
- **Container Images**: Optimized Dockerfiles for both runner and application
- **Kubernetes Orchestration**: Production-grade deployment with load balancing and rolling updates

The runner executes GitHub workflows in a self-hosted Kubernetes environment, enabling:
- Enhanced workflow control and customization
- Private/sensitive job execution
- Cost optimization for high-volume CI/CD operations
- Integration with proprietary tools and services

---

## Architecture

### System Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────────┐
│                        GitHub Repository                             │
│                    (Workflow Triggers)                               │
└────────────────────────────┬────────────────────────────────────────┘
                             │ Webhook/Trigger
                             ▼
         ┌───────────────────────────────────────┐
         │     GitHub Actions Service            │
         │   (Receives Workflow Job)              │
         └────────────┬────────────────────────┬─┘
                      │ Dispatch to            │
                      ▼                        ▼
    ┌─────────────────────────────┐  ┌───────────────────────────┐
    │  Kubernetes Cluster (AKS)   │  │  GitHub Hosted Runners    │
    │  (Self-Hosted Runners)      │  │  (Default Option)         │
    └─────┬───────────────────────┘  └───────────────────────────┘
          │
          ├─────────────────────────────────────┐
          │                                     │
    ┌─────▼──────────────┐    ┌────────────────▼──────┐
    │   Pod Replica 1    │    │   Pod Replica 2/3     │
    │ (Runner Container) │    │ (Runner Containers)   │
    │  - Java 21         │    │  - Runs Workflows     │
    │  - Maven           │    │  - Executes Tests     │
    │  - Python3         │    │  - Builds & Deploys   │
    └─────┬──────────────┘    └────────────┬──────────┘
          │                                │
          │         GitHub Runner Agent    │
          │         Listening for Jobs     │
          │                                │
          └────────────┬───────────────────┘
                       │
                ┌──────▼──────────┐
                │  News Feed App  │
                │ (Docker Image)  │
                │  - Java 21 JDK  │
                │  - Spring Boot  │
                │  - Port 8080    │
                └─────────────────┘
```

### Application Data Flow

```
┌────────────────┐
│ GitHub Workflow│
│   Triggered    │
└────────┬───────┘
         │
         ▼
┌────────────────────────┐
│  Kubernetes Runner Pod │
│  (Config & Register)   │
└────────┬───────────────┘
         │
         ▼
┌────────────────────────────┐
│ Execute Workflow Steps     │
│ 1. Checkout code          │
│ 2. Build Maven project    │
│ 3. Run Tests              │
│ 4. Build Docker image     │
│ 5. Push to Registry (ECR) │
└────────┬───────────────────┘
         │
         ▼
┌──────────────────────────────┐
│  Deploy News Feed App        │
│  - Pull from Docker Registry │
│  - Run Container on K8s      │
│  - Expose Service (Port 8080)│
└──────────┬───────────────────┘
           │
           ▼
┌──────────────────────────┐
│  Application Ready       │
│  Serving News Feeds      │
└──────────────────────────┘
```

---

## Components

### 1. **GitHub Actions Runner Container**

| File | Purpose |
|------|---------|
| `Dockerfile` | Main runner image with Java 21, Maven, Python3 |
| `entrypoint.sh` | Script to configure and start the runner |
| `Dockerfile1` | Alternative production image with vulnerabilities patched |

**Features:**
- Based on official GitHub Actions runner image
- Pre-installed development tools (Java 21, Maven, Python3)
- Automatic configuration on startup
- Ephemeral mode for security (pods cleaned up after job completion)

### 2. **News Feed Spring Boot Application**

| Directory | Purpose |
|-----------|---------|
| `news-feed/` | Spring Boot microservice |
| `src/main/java/` | Java source code |
| `src/main/resources/` | Configuration files |

**Key Classes:**
- `NewsFeedApplication.java`: Spring Boot entry point
- `NewsController.java`: REST endpoints for news categories
- `GoogleNewsService.java`: SerpAPI integration for news fetching

**Supported News Categories:**
- Technology
- Sports
- Business
- Global Economy
- War & Conflicts

### 3. **Kubernetes Deployment Configuration**

**File:** `runner-deployment.yaml`

```yaml
Key Configuration:
├── Replicas: 3 (High Availability)
├── Strategy: RollingUpdate (Zero-downtime updates)
│   ├── maxUnavailable: 1
│   └── maxSurge: 1
├── Environment Variables:
│   ├── REPO_URL: GitHub repository URL
│   ├── RUNNER_TOKEN: GitHub token from secrets
│   └── RUNNER_NAME: Unique pod identity
└── Container: github-runner image
```

### 4. **Secrets Management**

**File:** `secrets.yaml`

Stores sensitive data:
```
RUNNER_TOKEN: Your GitHub PAT (Personal Access Token)
```

---

## Prerequisites

### Required Tools & Access

- **GitHub Account** with repository access
- **Kubernetes Cluster** (AKS, EKS, GKE, or local Minikube)
- **Docker** installed (`docker --version`)
- **kubectl** CLI (`kubectl version --client`)
- **Java 21+** for local testing
- **Maven 3.6+** for building
- **SerpAPI Account** (free tier available) for news API access

### Installation Verification

```bash
# Verify installations
docker --version
kubectl version --client
java -version
mvn -version
```

---

## Implementation Steps

### Step 1: Generate GitHub Personal Access Token

1. Navigate to GitHub: https://github.com/settings/tokens
2. Click **"Generate new token"** → **"Tokens (classic)"**
3. Configure token scopes:
   - ✅ `repo` (full repository access)
   - ✅ `workflow` (GitHub Actions workflows)
   - ✅ `admin:org_hook` (if using organization repos)
4. Set expiration: **90 days** (recommended for security)
5. Click **"Generate token"** and **copy immediately** (not retrievable later)
6. Store safely: use later as `RUNNER_TOKEN`

### Step 2: Prepare Secrets Configuration

Update [secrets.yaml](secrets.yaml):

```bash
# Step 1: Encode your token in base64
echo -n "your_github_token_here" | base64
# Output: Z2hyX3RlbXBvcmFyeV90b2tlbmhlcmU=

# Step 2: Update secrets.yaml with encoded value
```

Updated `secrets.yaml`:
```yaml
apiVersion: v1
data:
  RUNNER_TOKEN: Z2hyX3RlbXBvcmFyeV90b2tlbmhlcmU=  # base64 encoded
kind: Secret
metadata:
  name: github-runner-secret
type: opaque
```

### Step 3: Build & Push Docker Image

#### Option A: Build Runner Image

```bash
# Navigate to project directory
cd Github_action-Runner

# Build the runner image
docker build -f Dockerfile -t your-registry/github-runner:v1 .

# Push to Docker registry (AWS ECR, Docker Hub, etc.)
docker push your-registry/github-runner:v1
```

#### Option B: Build News Feed Application Image

```bash
# Build the news-feed Maven project
cd news-feed
mvn clean package

# Build Docker image using Dockerfile1
docker build -f ../Dockerfile1 -t your-registry/news-feed:v1 .

# Push to registry
docker push your-registry/news-feed:v1
```

### Step 4: Update Kubernetes Manifest

Edit [runner-deployment.yaml](runner-deployment.yaml):

```yaml
spec:
  template:
    spec:
      containers:
      - name: runner
        image: your-registry/github-runner:v1  # ← Update image reference
        env:
        - name: REPO_URL
          value: "https://github.com/YOUR_ACCOUNT/YOUR_REPO"  # ← Update repo
        - name: RUNNER_TOKEN
          valueFrom:
            secretKeyRef:
              name: github-runner-secret
              key: RUNNER_TOKEN
```

### Step 5: Deploy to Kubernetes

```bash
# Step 1: Apply secrets
kubectl apply -f secrets.yaml
# Output: secret/github-runner-secret created

# Step 2: Apply deployment
kubectl apply -f runner-deployment.yaml
# Output: deployment.apps/github-runner3 created

# Step 3: Verify deployment
kubectl get pods -l app=github-runner3
# Output:
# github-runner3-abc123...   1/1   Running   0   45s
# github-runner3-def456...   1/1   Running   0   42s
# github-runner3-ghi789...   1/1   Running   0   40s

# Step 4: Check logs
kubectl logs -f deployment/github-runner3
```

### Step 6: Verify Runner Registration

1. Go to your GitHub repository
2. Navigate to **Settings** → **Actions** → **Runners**
3. You should see **3 runners** registered:
   - `github-runner3-{pod-id-1}`
   - `github-runner3-{pod-id-2}`
   - `github-runner3-{pod-id-3}`

All runners should show **Idle** status ✅

---

## Deployment Guide

### Supported Platforms

| Platform | Guide | Notes |
|----------|-------|-------|
| **AKS (Azure Kubernetes Service)** | See [Azure Deployment Guide](#azure-deployment) | Recommended for Azure environments |
| **EKS (AWS Elastic Kubernetes)** | Use ECR for image registry | AWS-native solution |
| **GKE (Google Kubernetes Engine)** | Use Google Artifact Registry | Google Cloud platform |
| **Minikube (Local Development)** | Perfect for testing | Single-machine cluster |

#### Azure Deployment

```bash
# Step 1: Create AKS cluster
az aks create \
  --resource-group myResourceGroup \
  --name myAKSCluster \
  --node-count 3 \
  --vm-set-type VirtualMachineScaleSets

# Step 2: Get credentials
az aks get-credentials \
  --resource-group myResourceGroup \
  --name myAKSCluster

# Step 3: Push image to ACR
az acr build \
  --registry myRegistry \
  --image github-runner:v1 .

# Step 4: Deploy using kubectl
kubectl apply -f secrets.yaml
kubectl apply -f runner-deployment.yaml
```

### Monitoring & Maintenance

```bash
# Monitor pod health
kubectl get pods -w

# View detailed pod info
kubectl describe pod github-runner3-abc123

# Stream logs in real-time
kubectl logs -f deployment/github-runner3 --all-containers

# Scale up runners if needed
kubectl scale deployment github-runner3 --replicas=5

# Rolling restart
kubectl rollout restart deployment/github-runner3

# Check deployment status
kubectl rollout status deployment/github-runner3
```

---

## Configuration

### Environment Variables

| Variable | Purpose | Example |
|----------|---------|---------|
| `REPO_URL` | GitHub repository URL | `https://github.com/user/repo` |
| `RUNNER_TOKEN` | GitHub PAT for runner registration | Stored in Kubernetes Secret |
| `RUNNER_NAME` | Unique runner identifier | Auto-generated from pod name |

### Application Configuration

**File:** `news-feed/src/main/resources/application.properties`

```properties
# SerpAPI Key for news fetching
serpapi.key=YOUR_SERPAPI_KEY

# Application port
server.port=8080

# Optional: Add more configuration
spring.application.name=news-feed
```

### Maven Configuration

**File:** `news-feed/settings.xml`

- Contains Maven plugin configurations
- Manages dependency repositories
- Defines build profiles

---

## Troubleshooting

### Issue 1: Runner pod in CrashLoopBackOff status

```bash
# Check logs
kubectl logs <pod-name>

# Common causes:
# 1. Invalid RUNNER_TOKEN
# 2. Wrong REPO_URL
# 3. GitHub API rate limiting

# Solution: Update secrets
kubectl delete secret github-runner-secret
kubectl apply -f secrets.yaml
kubectl rollout restart deployment/github-runner3
```

### Issue 2: Runners not appearing in GitHub UI

```bash
# Verify token is valid
curl -H "Authorization: token YOUR_TOKEN" \
  https://api.github.com/user

# Check runner logs for registration errors
kubectl logs -f deployment/github-runner3

# Recreate secret with correct token
kubectl delete secret github-runner-secret
# Update secrets.yaml with new token
kubectl apply -f secrets.yaml
```

### Issue 3: Workflows not executing on self-hosted runners

```bash
# In your workflow YAML, specify runs-on:
jobs:
  build:
    runs-on: [self-hosted]  # ← Add this label
    steps:
      - uses: actions/checkout@v3
      - run: mvn clean package
```

### Issue 4: Docker image push failures

```bash
# Verify Docker registry credentials
docker login your-registry.azurecr.io

# Check image exists locally
docker images | grep github-runner

# Re-tag and push
docker tag github-runner:v1 your-registry/github-runner:v1
docker push your-registry/github-runner:v1

# Verify in registry
az acr repository list --name yourRegistry
```

### Issue 5: News Feed application not accessible

```bash
# Check if pod is running
kubectl get pods -l app=news-feed

# Port forward for local testing
kubectl port-forward svc/news-feed 8080:8080

# Access at http://localhost:8080

# Check application logs
kubectl logs <news-feed-pod-name>

# Verify SerpAPI key is configured
kubectl describe pod <news-feed-pod-name> | grep -i env
```

---

## Workflow Integration Example

Create a GitHub Actions workflow to use this runner:

**`.github/workflows/build-deploy.yml`**

```yaml
name: Build & Deploy News Feed

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main]

jobs:
  build:
    runs-on: [self-hosted]  # Uses our Kubernetes runner
    
    steps:
    - uses: actions/checkout@v3
    
    - name: Set up Java
      uses: actions/setup-java@v3
      with:
        java-version: '21'
    
    - name: Build with Maven
      run: mvn clean package
    
    - name: Build Docker image
      run: |
        docker build -f Dockerfile1 -t news-feed:${{ github.sha }} .
        docker push your-registry/news-feed:${{ github.sha }}
    
    - name: Deploy to Kubernetes
      run: |
        kubectl set image deployment/news-feed \
          news-feed=your-registry/news-feed:${{ github.sha }}
        kubectl rollout status deployment/news-feed
```

---

## Summary

This setup provides:

✅ **Scalable CI/CD**: Run unlimited workflows on 3+ pods  
✅ **High Availability**: Rolling updates with zero downtime  
✅ **Security**: Ephemeral runners, secret management  
✅ **Integration**: Spring Boot microservice for news distribution  
✅ **Production-Ready**: Vulnerability-patched images, health checks  

For questions or support, refer to:
- [GitHub Actions Documentation](https://docs.github.com/en/actions)
- [Kubernetes Documentation](https://kubernetes.io/docs/)
- [Spring Boot Reference Guide](https://spring.io/projects/spring-boot)