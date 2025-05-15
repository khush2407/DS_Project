# Deployment Guide for Emotion Analysis System

This guide provides step-by-step instructions for deploying the entire Emotion Analysis System, including the backend, frontend, and machine learning model.

## Table of Contents

1. [Project Overview](#project-overview)
2. [Prerequisites](#prerequisites)
3. [Local Deployment](#local-deployment)
4. [Docker Deployment](#docker-deployment)
5. [Cloud Deployment](#cloud-deployment)
6. [Monitoring and Maintenance](#monitoring-and-maintenance)
7. [Troubleshooting](#troubleshooting)

## Project Overview

The Emotion Analysis System consists of:

- **Backend**: Python-based API service (Flask/FastAPI)
- **Frontend**: React with TypeScript
- **Machine Learning Model**: Emotion detection model
- **Database**: For user data and session management
- **Redis**: For caching (optional)

## Prerequisites

Before deploying, ensure you have the following installed:

- Python 3.8+ and pip
- Node.js 14+ and npm
- Docker and Docker Compose (for containerized deployment)
- Git

## Local Deployment

### 1. Clone the Repository

```bash
git clone <repository-url>
cd Distributed\ System
```

### 2. Backend Setup

#### Install Dependencies

```bash
cd backend
pip install -r requirements.txt
```

#### Configure Environment Variables

Create or update the `.env` file in the backend directory:

```
# Database configuration
DATABASE_URL=sqlite:///app.db

# Security
SECRET_KEY=your_secret_key_here
JWT_SECRET_KEY=your_jwt_secret_key_here

# Model paths
MODEL_PATH=../data/processed/emotion_model.pkl
FULL_MODEL_PATH=../models/emotion_detector
```

#### Run the Backend

```bash
python app.py
```

The backend should now be running on http://localhost:5000.

### 3. Frontend Setup

#### Install Dependencies

```bash
cd frontend
npm install
```

#### Configure Environment Variables

Create a `.env` file in the frontend directory:

```
REACT_APP_API_URL=http://localhost:5000
```

#### Run the Frontend

```bash
npm start
```

The frontend should now be running on http://localhost:3000.

## Docker Deployment

Docker allows you to containerize the entire application for easier deployment.

### 1. Build and Run with Docker Compose

```bash
docker-compose up --build
```

This will:
- Build the backend and frontend containers
- Set up a Redis container for caching
- Configure networking between containers
- Mount volumes for persistent data

### 2. Accessing the Application

- Frontend: http://localhost:3000
- Backend API: http://localhost:5000

## Cloud Deployment

### AWS Deployment

#### 1. Set Up AWS Resources

- Create an ECR repository for your Docker images
- Set up an ECS cluster or use Elastic Beanstalk
- Configure a load balancer
- Set up an RDS database (optional)
- Configure ElastiCache for Redis (optional)

#### 2. Push Docker Images to ECR

```bash
# Login to ECR
aws ecr get-login-password --region <region> | docker login --username AWS --password-stdin <aws-account-id>.dkr.ecr.<region>.amazonaws.com

# Tag images
docker tag emotion-backend:latest <aws-account-id>.dkr.ecr.<region>.amazonaws.com/emotion-backend:latest
docker tag emotion-frontend:latest <aws-account-id>.dkr.ecr.<region>.amazonaws.com/emotion-frontend:latest

# Push images
docker push <aws-account-id>.dkr.ecr.<region>.amazonaws.com/emotion-backend:latest
docker push <aws-account-id>.dkr.ecr.<region>.amazonaws.com/emotion-frontend:latest
```

#### 3. Deploy to ECS or Elastic Beanstalk

Follow AWS documentation for deploying containers to ECS or Elastic Beanstalk.

### Google Cloud Platform (GCP) Deployment

#### 1. Set Up GCP Resources

- Create a project in GCP
- Enable Container Registry or Artifact Registry
- Set up a GKE cluster or Cloud Run

#### 2. Push Docker Images to GCP

```bash
# Configure Docker to use gcloud as a credential helper
gcloud auth configure-docker

# Tag images
docker tag emotion-backend:latest gcr.io/<project-id>/emotion-backend:latest
docker tag emotion-frontend:latest gcr.io/<project-id>/emotion-frontend:latest

# Push images
docker push gcr.io/<project-id>/emotion-backend:latest
docker push gcr.io/<project-id>/emotion-frontend:latest
```

#### 3. Deploy to GKE or Cloud Run

Follow GCP documentation for deploying containers to GKE or Cloud Run.

### Microsoft Azure Deployment

#### 1. Set Up Azure Resources

- Create a resource group
- Set up Azure Container Registry
- Configure Azure Kubernetes Service or App Service

#### 2. Push Docker Images to Azure

```bash
# Login to Azure Container Registry
az acr login --name <registry-name>

# Tag images
docker tag emotion-backend:latest <registry-name>.azurecr.io/emotion-backend:latest
docker tag emotion-frontend:latest <registry-name>.azurecr.io/emotion-frontend:latest

# Push images
docker push <registry-name>.azurecr.io/emotion-backend:latest
docker push <registry-name>.azurecr.io/emotion-frontend:latest
```

#### 3. Deploy to AKS or App Service

Follow Azure documentation for deploying containers to AKS or App Service.

## Monitoring and Maintenance

### 1. Logging

- Configure logging in the backend using the built-in logging module
- Set up log aggregation using tools like ELK Stack, Graylog, or cloud-native solutions

### 2. Monitoring

- Set up health checks for both backend and frontend
- Use monitoring tools like Prometheus and Grafana
- Configure alerts for critical issues

### 3. Updating the Model

To update the emotion detection model:

1. Train a new model using the scripts in the `scripts` directory
2. Replace the model files in `data/processed/emotion_model.pkl` and `models/emotion_detector/`
3. Restart the backend service or redeploy the containers

## Troubleshooting

### Common Issues

#### Backend Won't Start

- Check if all dependencies are installed: `pip install -r requirements.txt`
- Verify environment variables are set correctly
- Check if the model files exist in the specified paths

#### Frontend Won't Connect to Backend

- Ensure the backend is running and accessible
- Check if CORS is configured correctly in the backend
- Verify the API URL in the frontend environment variables

#### Docker Issues

- Ensure Docker and Docker Compose are installed and running
- Check Docker logs: `docker-compose logs`
- Verify port mappings and network configurations

#### Model Loading Issues

- Check if the model files exist and are in the correct format
- Verify the paths in the environment variables
- Check backend logs for specific error messages

## Additional Resources

- [Docker Documentation](https://docs.docker.com/)
- [AWS Deployment Guide](https://aws.amazon.com/getting-started/hands-on/deploy-docker-containers/)
- [GCP Deployment Guide](https://cloud.google.com/run/docs/quickstarts/build-and-deploy)
- [Azure Deployment Guide](https://docs.microsoft.com/en-us/azure/app-service/tutorial-custom-container)