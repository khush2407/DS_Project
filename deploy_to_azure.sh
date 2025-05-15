#!/bin/bash

# Deployment script for the Emotion Analysis System to Microsoft Azure
# This script automates the deployment process to Azure using ACR and AKS

# Exit on error
set -e

# Configuration
RESOURCE_GROUP="emotion-analysis-rg"
LOCATION="eastus"  # Change to your preferred location
ACR_NAME="emotionanalysisacr"  # Must be globally unique
AKS_CLUSTER_NAME="emotion-analysis-aks"
MONGODB_URI="mongodb://mongodb:27017/wellness_app"
SECRET_KEY="your-secret-key-here"  # Replace with your secret key

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Function to print colored output
print_message() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if Azure CLI is installed
if ! command -v az &> /dev/null; then
    print_error "Azure CLI is not installed. Please install it first."
    exit 1
fi

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    print_error "Docker is not installed. Please install it first."
    exit 1
fi

# Check if kubectl is installed
if ! command -v kubectl &> /dev/null; then
    print_error "kubectl is not installed. Please install it first."
    exit 1
fi

# Check if user is logged in to Azure
print_message "Checking Azure credentials..."
if ! az account show &> /dev/null; then
    print_error "Not logged in to Azure. Please run 'az login' first."
    exit 1
fi

# Step 1: Create resource group if it doesn't exist
print_message "Creating resource group if it doesn't exist..."
az group create --name $RESOURCE_GROUP --location $LOCATION

# Step 2: Create Azure Container Registry (ACR) if it doesn't exist
print_message "Creating Azure Container Registry if it doesn't exist..."
az acr create --resource-group $RESOURCE_GROUP --name $ACR_NAME --sku Basic

# Step 3: Log in to ACR
print_message "Logging in to ACR..."
az acr login --name $ACR_NAME

# Step 4: Build Docker images
print_message "Building Docker images..."
docker-compose -f docker/docker-compose.yml build

# Step 5: Tag Docker images
print_message "Tagging Docker images..."
ACR_LOGIN_SERVER=$(az acr show --name $ACR_NAME --query loginServer --output tsv)
ACR_BACKEND_URI="$ACR_LOGIN_SERVER/emotion-backend:latest"
ACR_FRONTEND_URI="$ACR_LOGIN_SERVER/emotion-frontend:latest"

docker tag emotion-backend:latest $ACR_BACKEND_URI
docker tag emotion-frontend:latest $ACR_FRONTEND_URI

# Step 6: Push Docker images to ACR
print_message "Pushing Docker images to ACR..."
docker push $ACR_BACKEND_URI
docker push $ACR_FRONTEND_URI

# Step 7: Create AKS cluster if it doesn't exist
print_message "Creating AKS cluster if it doesn't exist..."
if ! az aks show --resource-group $RESOURCE_GROUP --name $AKS_CLUSTER_NAME &> /dev/null; then
    print_message "Creating AKS cluster $AKS_CLUSTER_NAME..."
    az aks create \
        --resource-group $RESOURCE_GROUP \
        --name $AKS_CLUSTER_NAME \
        --node-count 2 \
        --enable-addons monitoring \
        --generate-ssh-keys \
        --attach-acr $ACR_NAME
else
    print_message "AKS cluster $AKS_CLUSTER_NAME already exists."
    # Ensure ACR is attached to AKS
    az aks update --resource-group $RESOURCE_GROUP --name $AKS_CLUSTER_NAME --attach-acr $ACR_NAME
fi

# Step 8: Get credentials for the AKS cluster
print_message "Getting credentials for the AKS cluster..."
az aks get-credentials --resource-group $RESOURCE_GROUP --name $AKS_CLUSTER_NAME

# Step 9: Create Kubernetes namespace
print_message "Creating Kubernetes namespace..."
kubectl create namespace emotion-analysis || true

# Step 10: Create Kubernetes secrets
print_message "Creating Kubernetes secrets..."
kubectl create secret generic emotion-analysis-secrets \
    --namespace=emotion-analysis \
    --from-literal=mongodb-uri=$MONGODB_URI \
    --from-literal=secret-key=$SECRET_KEY \
    --dry-run=client -o yaml | kubectl apply -f -

# Step 11: Create Kubernetes deployment and service files
print_message "Creating Kubernetes deployment and service files..."

# Create MongoDB deployment and service
cat > mongodb-deployment.yaml << EOF
apiVersion: apps/v1
kind: Deployment
metadata:
  name: mongodb
  namespace: emotion-analysis
spec:
  selector:
    matchLabels:
      app: mongodb
  replicas: 1
  template:
    metadata:
      labels:
        app: mongodb
    spec:
      containers:
      - name: mongodb
        image: mongo:latest
        ports:
        - containerPort: 27017
        volumeMounts:
        - name: mongodb-data
          mountPath: /data/db
      volumes:
      - name: mongodb-data
        persistentVolumeClaim:
          claimName: mongodb-pvc
---
apiVersion: v1
kind: Service
metadata:
  name: mongodb
  namespace: emotion-analysis
spec:
  selector:
    app: mongodb
  ports:
  - port: 27017
    targetPort: 27017
  type: ClusterIP
---
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: mongodb-pvc
  namespace: emotion-analysis
spec:
  accessModes:
    - ReadWriteOnce
  resources:
    requests:
      storage: 10Gi
EOF

# Create Redis deployment and service
cat > redis-deployment.yaml << EOF
apiVersion: apps/v1
kind: Deployment
metadata:
  name: redis
  namespace: emotion-analysis
spec:
  selector:
    matchLabels:
      app: redis
  replicas: 1
  template:
    metadata:
      labels:
        app: redis
    spec:
      containers:
      - name: redis
        image: redis:alpine
        ports:
        - containerPort: 6379
---
apiVersion: v1
kind: Service
metadata:
  name: redis
  namespace: emotion-analysis
spec:
  selector:
    app: redis
  ports:
  - port: 6379
    targetPort: 6379
  type: ClusterIP
EOF

# Create backend deployment and service
cat > backend-deployment.yaml << EOF
apiVersion: apps/v1
kind: Deployment
metadata:
  name: backend
  namespace: emotion-analysis
spec:
  selector:
    matchLabels:
      app: backend
  replicas: 1
  template:
    metadata:
      labels:
        app: backend
    spec:
      containers:
      - name: backend
        image: $ACR_BACKEND_URI
        ports:
        - containerPort: 8000
        env:
        - name: MONGODB_URI
          valueFrom:
            secretKeyRef:
              name: emotion-analysis-secrets
              key: mongodb-uri
        - name: SECRET_KEY
          valueFrom:
            secretKeyRef:
              name: emotion-analysis-secrets
              key: secret-key
        - name: MODEL_PATH
          value: "/app/data/processed/emotion_model.pkl"
        volumeMounts:
        - name: model-data
          mountPath: /app/data
      volumes:
      - name: model-data
        emptyDir: {}
---
apiVersion: v1
kind: Service
metadata:
  name: backend
  namespace: emotion-analysis
spec:
  selector:
    app: backend
  ports:
  - port: 8000
    targetPort: 8000
  type: ClusterIP
EOF

# Create frontend deployment and service
cat > frontend-deployment.yaml << EOF
apiVersion: apps/v1
kind: Deployment
metadata:
  name: frontend
  namespace: emotion-analysis
spec:
  selector:
    matchLabels:
      app: frontend
  replicas: 1
  template:
    metadata:
      labels:
        app: frontend
    spec:
      containers:
      - name: frontend
        image: $ACR_FRONTEND_URI
        ports:
        - containerPort: 3000
        env:
        - name: REACT_APP_API_URL
          value: "http://backend:8000"
---
apiVersion: v1
kind: Service
metadata:
  name: frontend
  namespace: emotion-analysis
spec:
  selector:
    app: frontend
  ports:
  - port: 3000
    targetPort: 3000
  type: LoadBalancer
EOF

# Step 12: Apply Kubernetes configurations
print_message "Applying Kubernetes configurations..."
kubectl apply -f mongodb-deployment.yaml
kubectl apply -f redis-deployment.yaml
kubectl apply -f backend-deployment.yaml
kubectl apply -f frontend-deployment.yaml

# Step 13: Wait for deployments to be ready
print_message "Waiting for deployments to be ready..."
kubectl wait --namespace=emotion-analysis --for=condition=available --timeout=300s deployment/mongodb
kubectl wait --namespace=emotion-analysis --for=condition=available --timeout=300s deployment/redis
kubectl wait --namespace=emotion-analysis --for=condition=available --timeout=300s deployment/backend
kubectl wait --namespace=emotion-analysis --for=condition=available --timeout=300s deployment/frontend

# Step 14: Get the external IP of the frontend service
print_message "Getting external IP of the frontend service..."
FRONTEND_IP=""
while [ -z "$FRONTEND_IP" ]; do
    FRONTEND_IP=$(kubectl get service frontend --namespace=emotion-analysis -o jsonpath='{.status.loadBalancer.ingress[0].ip}')
    if [ -z "$FRONTEND_IP" ]; then
        print_message "Waiting for external IP..."
        sleep 10
    fi
done

print_message "Deployment completed successfully!"
print_message "Frontend: http://$FRONTEND_IP:3000"
print_message "Backend API: http://$FRONTEND_IP:8000 (via internal service)"

# Clean up
rm -f mongodb-deployment.yaml redis-deployment.yaml backend-deployment.yaml frontend-deployment.yaml

print_warning "Note: This is a basic deployment. For production, consider:"
print_warning "- Using Azure Cosmos DB for MongoDB instead of containerized MongoDB"
print_warning "- Using Azure Cache for Redis instead of containerized Redis"
print_warning "- Setting up Azure Application Gateway for ingress"
print_warning "- Setting up Azure Key Vault for secrets management"
print_warning "- Configuring HTTPS with Azure-managed certificates"
print_warning "- Setting up Azure Monitor for monitoring and logging"