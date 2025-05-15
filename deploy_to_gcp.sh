#!/bin/bash

# Deployment script for the Emotion Analysis System to Google Cloud Platform
# This script automates the deployment process to GCP using GCR and GKE

# Exit on error
set -e

# Configuration
PROJECT_ID="your-gcp-project-id"  # Change to your GCP project ID
GCR_HOSTNAME="gcr.io"
BACKEND_IMAGE_NAME="emotion-backend"
FRONTEND_IMAGE_NAME="emotion-frontend"
GKE_CLUSTER_NAME="emotion-analysis-cluster"
GKE_ZONE="us-central1-a"  # Change to your preferred zone
GKE_REGION="us-central1"  # Change to your preferred region
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

# Check if gcloud CLI is installed
if ! command -v gcloud &> /dev/null; then
    print_error "Google Cloud SDK is not installed. Please install it first."
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

# Check if user is logged in to GCP
print_message "Checking GCP credentials..."
if ! gcloud auth print-access-token &> /dev/null; then
    print_error "Not logged in to GCP. Please run 'gcloud auth login' first."
    exit 1
fi

# Step 1: Set the GCP project
print_message "Setting GCP project to $PROJECT_ID..."
gcloud config set project $PROJECT_ID

# Step 2: Enable required APIs
print_message "Enabling required GCP APIs..."
gcloud services enable container.googleapis.com containerregistry.googleapis.com

# Step 3: Configure Docker to use gcloud as a credential helper
print_message "Configuring Docker to use gcloud as a credential helper..."
gcloud auth configure-docker

# Step 4: Build Docker images
print_message "Building Docker images..."
docker-compose -f docker/docker-compose.yml build

# Step 5: Tag Docker images
print_message "Tagging Docker images..."
GCR_BACKEND_URI="$GCR_HOSTNAME/$PROJECT_ID/$BACKEND_IMAGE_NAME:latest"
GCR_FRONTEND_URI="$GCR_HOSTNAME/$PROJECT_ID/$FRONTEND_IMAGE_NAME:latest"

docker tag emotion-backend:latest $GCR_BACKEND_URI
docker tag emotion-frontend:latest $GCR_FRONTEND_URI

# Step 6: Push Docker images to GCR
print_message "Pushing Docker images to GCR..."
docker push $GCR_BACKEND_URI
docker push $GCR_FRONTEND_URI

# Step 7: Create GKE cluster if it doesn't exist
print_message "Creating GKE cluster if it doesn't exist..."
if ! gcloud container clusters describe $GKE_CLUSTER_NAME --zone $GKE_ZONE &> /dev/null; then
    print_message "Creating GKE cluster $GKE_CLUSTER_NAME..."
    gcloud container clusters create $GKE_CLUSTER_NAME \
        --zone $GKE_ZONE \
        --num-nodes=2 \
        --machine-type=e2-standard-2
else
    print_message "GKE cluster $GKE_CLUSTER_NAME already exists."
fi

# Step 8: Get credentials for the GKE cluster
print_message "Getting credentials for the GKE cluster..."
gcloud container clusters get-credentials $GKE_CLUSTER_NAME --zone $GKE_ZONE

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
        image: $GCR_BACKEND_URI
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
        image: $GCR_FRONTEND_URI
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
print_warning "- Setting up Cloud Memorystore for Redis"
print_warning "- Using Cloud SQL or MongoDB Atlas instead of containerized MongoDB"
print_warning "- Setting up proper IAM roles and permissions"
print_warning "- Configuring HTTPS with Google-managed certificates"
print_warning "- Setting up Cloud Monitoring and Logging"