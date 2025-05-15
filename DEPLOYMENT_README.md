# Emotion Analysis System Deployment

This document provides instructions for deploying the Emotion Analysis System to various cloud platforms.

## Deployment Options

The system can be deployed to the following cloud platforms:

1. **AWS (Amazon Web Services)** - Using ECR and ECS
2. **GCP (Google Cloud Platform)** - Using GCR and GKE
3. **Azure** - Using ACR and AKS
4. **Local** - Using Docker Compose

## Prerequisites

Before deploying, ensure you have the following installed:

- Docker and Docker Compose
- Cloud provider CLI tools:
  - AWS CLI for AWS deployment
  - Google Cloud SDK for GCP deployment
  - Azure CLI for Azure deployment
- kubectl for Kubernetes deployments (GCP and Azure)
- Git

## Local Deployment

For local development and testing, use Docker Compose:

```bash
# Clone the repository (if you haven't already)
git clone <repository-url>
cd Distributed\ System

# Build and run the containers
docker-compose -f docker/docker-compose.yml up --build
```

The application will be available at:
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000

## Cloud Deployment

### 1. AWS Deployment

To deploy to AWS using ECR and ECS:

```bash
# Make the script executable
chmod +x deploy_to_aws.sh

# Edit the script to update configuration variables
# - AWS_REGION: Your preferred AWS region
# - MONGODB_URI: Your MongoDB connection string
# - SECRET_KEY: Your secret key for the application

# Run the deployment script
./deploy_to_aws.sh
```

The script will:
1. Create ECR repositories for the backend and frontend images
2. Build and push Docker images to ECR
3. Create an ECS cluster and task definition
4. Deploy the application to ECS
5. Output the URLs for accessing the application

### 2. GCP Deployment

To deploy to Google Cloud Platform using GCR and GKE:

```bash
# Make the script executable
chmod +x deploy_to_gcp.sh

# Edit the script to update configuration variables
# - PROJECT_ID: Your GCP project ID
# - GKE_ZONE: Your preferred GCP zone
# - GKE_REGION: Your preferred GCP region
# - MONGODB_URI: Your MongoDB connection string
# - SECRET_KEY: Your secret key for the application

# Run the deployment script
./deploy_to_gcp.sh
```

The script will:
1. Enable required GCP APIs
2. Build and push Docker images to GCR
3. Create a GKE cluster
4. Deploy the application to GKE
5. Output the URLs for accessing the application

### 3. Azure Deployment

To deploy to Microsoft Azure using ACR and AKS:

```bash
# Make the script executable
chmod +x deploy_to_azure.sh

# Edit the script to update configuration variables
# - RESOURCE_GROUP: Your Azure resource group name
# - LOCATION: Your preferred Azure location
# - ACR_NAME: Your Azure Container Registry name
# - AKS_CLUSTER_NAME: Your Azure Kubernetes Service cluster name
# - MONGODB_URI: Your MongoDB connection string
# - SECRET_KEY: Your secret key for the application

# Run the deployment script
./deploy_to_azure.sh
```

The script will:
1. Create a resource group and ACR
2. Build and push Docker images to ACR
3. Create an AKS cluster
4. Deploy the application to AKS
5. Output the URLs for accessing the application

## Production Considerations

The deployment scripts provided are intended for demonstration and development purposes. For production deployments, consider the following:

### AWS Production Deployment

- Use AWS RDS for MongoDB instead of containerized MongoDB
- Use AWS ElastiCache for Redis instead of containerized Redis
- Set up an Application Load Balancer (ALB) for the frontend and backend
- Use AWS Certificate Manager for HTTPS
- Set up CloudWatch for monitoring and logging
- Use AWS Secrets Manager for secrets management
- Set up proper IAM roles and permissions
- Configure auto-scaling for the ECS services

### GCP Production Deployment

- Use Cloud SQL or MongoDB Atlas for MongoDB instead of containerized MongoDB
- Use Cloud Memorystore for Redis instead of containerized Redis
- Set up Cloud Load Balancing for the frontend and backend
- Use Google-managed certificates for HTTPS
- Set up Cloud Monitoring and Logging
- Use Secret Manager for secrets management
- Set up proper IAM roles and permissions
- Configure auto-scaling for the GKE deployments

### Azure Production Deployment

- Use Azure Cosmos DB for MongoDB instead of containerized MongoDB
- Use Azure Cache for Redis instead of containerized Redis
- Set up Azure Application Gateway for ingress
- Use Azure-managed certificates for HTTPS
- Set up Azure Monitor for monitoring and logging
- Use Azure Key Vault for secrets management
- Set up proper IAM roles and permissions
- Configure auto-scaling for the AKS deployments

## Troubleshooting

### Common Issues

#### Docker Build Failures

If Docker build fails, check:
- Docker daemon is running
- You have sufficient permissions
- Internet connection is stable for downloading dependencies

#### Cloud Authentication Issues

If authentication fails:
- AWS: Run `aws configure` to set up credentials
- GCP: Run `gcloud auth login` to authenticate
- Azure: Run `az login` to authenticate

#### Deployment Failures

If deployment fails:
- Check cloud provider quotas and limits
- Verify network connectivity
- Check for syntax errors in Kubernetes manifests
- Review cloud provider console for specific error messages

## Maintenance

### Updating the Application

To update the application:

1. Make changes to the code
2. Rebuild the Docker images
3. Push the new images to the container registry
4. Update the Kubernetes deployments or ECS services

### Monitoring

Monitor the application using:
- AWS: CloudWatch
- GCP: Cloud Monitoring
- Azure: Azure Monitor

### Backup and Recovery

Set up regular backups of:
- MongoDB data
- Application configuration
- Container images

## Support

For issues with the deployment scripts, please open an issue in the repository or contact the development team.