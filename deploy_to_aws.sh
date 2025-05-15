#!/bin/bash

# Deployment script for the Emotion Analysis System to AWS
# This script automates the deployment process to AWS using ECR and ECS

# Exit on error
set -e

# Configuration
AWS_REGION="us-east-1"  # Change to your preferred region
ECR_REPOSITORY_BACKEND="emotion-backend"
ECR_REPOSITORY_FRONTEND="emotion-frontend"
ECS_CLUSTER_NAME="emotion-analysis-cluster"
ECS_SERVICE_NAME="emotion-analysis-service"
ECS_TASK_FAMILY="emotion-analysis-task"
MONGODB_URI="mongodb://your-mongodb-uri"  # Replace with your MongoDB URI
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

# Check if AWS CLI is installed
if ! command -v aws &> /dev/null; then
    print_error "AWS CLI is not installed. Please install it first."
    exit 1
fi

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    print_error "Docker is not installed. Please install it first."
    exit 1
fi

# Check if user is logged in to AWS
print_message "Checking AWS credentials..."
if ! aws sts get-caller-identity &> /dev/null; then
    print_error "Not logged in to AWS. Please run 'aws configure' first."
    exit 1
fi

# Step 1: Create ECR repositories if they don't exist
print_message "Creating ECR repositories if they don't exist..."
aws ecr describe-repositories --repository-names $ECR_REPOSITORY_BACKEND &> /dev/null || \
    aws ecr create-repository --repository-name $ECR_REPOSITORY_BACKEND
aws ecr describe-repositories --repository-names $ECR_REPOSITORY_FRONTEND &> /dev/null || \
    aws ecr create-repository --repository-name $ECR_REPOSITORY_FRONTEND

# Step 2: Get ECR login token
print_message "Logging in to ECR..."
aws ecr get-login-password --region $AWS_REGION | docker login --username AWS --password-stdin $(aws sts get-caller-identity --query Account --output text).dkr.ecr.$AWS_REGION.amazonaws.com

# Step 3: Build Docker images
print_message "Building Docker images..."
docker-compose -f docker/docker-compose.yml build

# Step 4: Tag Docker images
print_message "Tagging Docker images..."
ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)
ECR_BACKEND_URI="$ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com/$ECR_REPOSITORY_BACKEND:latest"
ECR_FRONTEND_URI="$ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com/$ECR_REPOSITORY_FRONTEND:latest"

docker tag emotion-backend:latest $ECR_BACKEND_URI
docker tag emotion-frontend:latest $ECR_FRONTEND_URI

# Step 5: Push Docker images to ECR
print_message "Pushing Docker images to ECR..."
docker push $ECR_BACKEND_URI
docker push $ECR_FRONTEND_URI

# Step 6: Create ECS cluster if it doesn't exist
print_message "Creating ECS cluster if it doesn't exist..."
aws ecs describe-clusters --clusters $ECS_CLUSTER_NAME &> /dev/null || \
    aws ecs create-cluster --cluster-name $ECS_CLUSTER_NAME

# Step 7: Create task definition
print_message "Creating ECS task definition..."
cat > task-definition.json << EOF
{
    "family": "$ECS_TASK_FAMILY",
    "networkMode": "awsvpc",
    "executionRoleArn": "arn:aws:iam::$ACCOUNT_ID:role/ecsTaskExecutionRole",
    "containerDefinitions": [
        {
            "name": "backend",
            "image": "$ECR_BACKEND_URI",
            "essential": true,
            "portMappings": [
                {
                    "containerPort": 8000,
                    "hostPort": 8000,
                    "protocol": "tcp"
                }
            ],
            "environment": [
                {
                    "name": "MONGODB_URI",
                    "value": "$MONGODB_URI"
                },
                {
                    "name": "SECRET_KEY",
                    "value": "$SECRET_KEY"
                },
                {
                    "name": "MODEL_PATH",
                    "value": "/app/data/processed/emotion_model.pkl"
                }
            ],
            "logConfiguration": {
                "logDriver": "awslogs",
                "options": {
                    "awslogs-group": "/ecs/$ECS_TASK_FAMILY",
                    "awslogs-region": "$AWS_REGION",
                    "awslogs-stream-prefix": "backend"
                }
            }
        },
        {
            "name": "frontend",
            "image": "$ECR_FRONTEND_URI",
            "essential": true,
            "portMappings": [
                {
                    "containerPort": 3000,
                    "hostPort": 3000,
                    "protocol": "tcp"
                }
            ],
            "environment": [
                {
                    "name": "REACT_APP_API_URL",
                    "value": "http://localhost:8000"
                }
            ],
            "logConfiguration": {
                "logDriver": "awslogs",
                "options": {
                    "awslogs-group": "/ecs/$ECS_TASK_FAMILY",
                    "awslogs-region": "$AWS_REGION",
                    "awslogs-stream-prefix": "frontend"
                }
            }
        },
        {
            "name": "mongodb",
            "image": "mongo:latest",
            "essential": true,
            "portMappings": [
                {
                    "containerPort": 27017,
                    "hostPort": 27017,
                    "protocol": "tcp"
                }
            ],
            "mountPoints": [
                {
                    "sourceVolume": "mongodb-data",
                    "containerPath": "/data/db"
                }
            ],
            "logConfiguration": {
                "logDriver": "awslogs",
                "options": {
                    "awslogs-group": "/ecs/$ECS_TASK_FAMILY",
                    "awslogs-region": "$AWS_REGION",
                    "awslogs-stream-prefix": "mongodb"
                }
            }
        },
        {
            "name": "redis",
            "image": "redis:alpine",
            "essential": true,
            "portMappings": [
                {
                    "containerPort": 6379,
                    "hostPort": 6379,
                    "protocol": "tcp"
                }
            ],
            "logConfiguration": {
                "logDriver": "awslogs",
                "options": {
                    "awslogs-group": "/ecs/$ECS_TASK_FAMILY",
                    "awslogs-region": "$AWS_REGION",
                    "awslogs-stream-prefix": "redis"
                }
            }
        }
    ],
    "volumes": [
        {
            "name": "mongodb-data",
            "dockerVolumeConfiguration": {
                "scope": "shared",
                "autoprovision": true,
                "driver": "local"
            }
        }
    ],
    "requiresCompatibilities": [
        "FARGATE"
    ],
    "cpu": "1024",
    "memory": "2048"
}
EOF

# Register task definition
TASK_DEFINITION_ARN=$(aws ecs register-task-definition --cli-input-json file://task-definition.json --query 'taskDefinition.taskDefinitionArn' --output text)
print_message "Task definition registered: $TASK_DEFINITION_ARN"

# Step 8: Create CloudWatch log group
print_message "Creating CloudWatch log group..."
aws logs create-log-group --log-group-name "/ecs/$ECS_TASK_FAMILY" || true

# Step 9: Create security group for the ECS service
print_message "Creating security group..."
VPC_ID=$(aws ec2 describe-vpcs --query 'Vpcs[0].VpcId' --output text)
SECURITY_GROUP_ID=$(aws ec2 create-security-group --group-name "$ECS_SERVICE_NAME-sg" --description "Security group for $ECS_SERVICE_NAME" --vpc-id $VPC_ID --query 'GroupId' --output text || aws ec2 describe-security-groups --filters "Name=group-name,Values=$ECS_SERVICE_NAME-sg" --query 'SecurityGroups[0].GroupId' --output text)

# Allow inbound traffic on ports 3000 and 8000
aws ec2 authorize-security-group-ingress --group-id $SECURITY_GROUP_ID --protocol tcp --port 3000 --cidr 0.0.0.0/0 || true
aws ec2 authorize-security-group-ingress --group-id $SECURITY_GROUP_ID --protocol tcp --port 8000 --cidr 0.0.0.0/0 || true
aws ec2 authorize-security-group-ingress --group-id $SECURITY_GROUP_ID --protocol tcp --port 27017 --cidr 0.0.0.0/0 || true
aws ec2 authorize-security-group-ingress --group-id $SECURITY_GROUP_ID --protocol tcp --port 6379 --cidr 0.0.0.0/0 || true

# Step 10: Get subnet IDs
print_message "Getting subnet IDs..."
SUBNET_IDS=$(aws ec2 describe-subnets --query 'Subnets[0:2].SubnetId' --output text | tr '\t' ',')

# Step 11: Create ECS service
print_message "Creating ECS service..."
aws ecs create-service \
    --cluster $ECS_CLUSTER_NAME \
    --service-name $ECS_SERVICE_NAME \
    --task-definition $TASK_DEFINITION_ARN \
    --desired-count 1 \
    --launch-type FARGATE \
    --network-configuration "awsvpcConfiguration={subnets=[$SUBNET_IDS],securityGroups=[$SECURITY_GROUP_ID],assignPublicIp=ENABLED}" \
    --scheduling-strategy REPLICA || \
aws ecs update-service \
    --cluster $ECS_CLUSTER_NAME \
    --service $ECS_SERVICE_NAME \
    --task-definition $TASK_DEFINITION_ARN \
    --desired-count 1 \
    --network-configuration "awsvpcConfiguration={subnets=[$SUBNET_IDS],securityGroups=[$SECURITY_GROUP_ID],assignPublicIp=ENABLED}"

# Step 12: Wait for service to stabilize
print_message "Waiting for service to stabilize..."
aws ecs wait services-stable --cluster $ECS_CLUSTER_NAME --services $ECS_SERVICE_NAME

# Step 13: Get the public IP of the task
print_message "Getting public IP of the task..."
TASK_ARN=$(aws ecs list-tasks --cluster $ECS_CLUSTER_NAME --service-name $ECS_SERVICE_NAME --query 'taskArns[0]' --output text)
NETWORK_INTERFACE=$(aws ecs describe-tasks --cluster $ECS_CLUSTER_NAME --tasks $TASK_ARN --query 'tasks[0].attachments[0].details[?name==`networkInterfaceId`].value' --output text)
PUBLIC_IP=$(aws ec2 describe-network-interfaces --network-interface-ids $NETWORK_INTERFACE --query 'NetworkInterfaces[0].Association.PublicIp' --output text)

print_message "Deployment completed successfully!"
print_message "Backend API: http://$PUBLIC_IP:8000"
print_message "Frontend: http://$PUBLIC_IP:3000"

# Clean up
rm -f task-definition.json

print_warning "Note: This is a basic deployment. For production, consider:"
print_warning "- Setting up a load balancer"
print_warning "- Using AWS RDS instead of containerized MongoDB"
print_warning "- Using AWS ElastiCache instead of containerized Redis"
print_warning "- Setting up proper IAM roles and permissions"
print_warning "- Configuring HTTPS with AWS Certificate Manager"