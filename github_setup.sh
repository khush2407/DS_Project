#!/bin/bash

# Script to initialize a Git repository, commit all files, and push to GitHub
# Make sure to replace YOUR_USERNAME and YOUR_REPOSITORY_NAME with your actual GitHub username and repository name

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

# Check if Git is installed
if ! command -v git &> /dev/null; then
    print_error "Git is not installed. Please install it first."
    exit 1
fi

# Step 1: Create a .gitignore file to exclude unnecessary files
print_message "Creating .gitignore file..."
cat > .gitignore << EOF
# Node.js
node_modules/
npm-debug.log
yarn-debug.log
yarn-error.log
.pnp/
.pnp.js
.npm

# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
env/
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
*.egg-info/
.installed.cfg
*.egg
.pytest_cache/
.coverage
htmlcov/

# Environment variables
.env
.env.local
.env.development.local
.env.test.local
.env.production.local

# IDE
.idea/
.vscode/
*.swp
*.swo
.DS_Store

# Docker
.docker/

# Data
data/raw/
data/processed/
*.pkl
*.csv
*.json
*.log

# Misc
.DS_Store
.env.local
.env.development.local
.env.test.local
.env.production.local
EOF

# Step 2: Initialize Git repository
print_message "Initializing Git repository..."
git init

# Step 3: Add all files to staging
print_message "Adding files to staging..."
git add .

# Step 4: Create initial commit
print_message "Creating initial commit..."
git commit -m "Initial commit: Emotion Analysis System"

# Step 5: Create a README.md file if it doesn't exist
if [ ! -f README.md ]; then
    print_message "Creating README.md file..."
    cat > README.md << EOF
# Emotion Analysis System

A distributed system for emotion detection and wellness recommendations.

## Features

- Emotion detection from text
- Personalized wellness recommendations
- User authentication and session management
- Activity tracking and history
- Emotion trends analysis

## Components

- Backend: Python FastAPI application
- Frontend: React with TypeScript
- Database: MongoDB
- Cache: Redis
- Machine Learning: Emotion detection model

## Deployment

See the [Deployment Guide](DEPLOYMENT_GUIDE.md) for instructions on deploying the system.

## Development

See the [Development Guide](DEPLOYMENT_README.md) for instructions on setting up the development environment.
EOF

    # Add README.md to staging
    git add README.md
    git commit -m "Add README.md"
fi

# Step 6: Set up GitHub repository
print_message "Now you need to create a repository on GitHub."
print_message "Go to https://github.com/new and create a new repository."
print_message "Do not initialize it with a README, .gitignore, or license."
print_message "Once created, run the following commands to push your code:"
print_message ""
print_message "git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPOSITORY_NAME.git"
print_message "git branch -M main"
print_message "git push -u origin main"
print_message ""
print_warning "Replace YOUR_USERNAME and YOUR_REPOSITORY_NAME with your actual GitHub username and repository name."

# Ask if the user wants to push to GitHub now
read -p "Have you created the GitHub repository? (y/n): " created_repo
if [ "$created_repo" = "y" ]; then
    read -p "Enter your GitHub username: " github_username
    read -p "Enter your repository name: " repo_name
    
    # Step 7: Add GitHub remote
    print_message "Adding GitHub remote..."
    git remote add origin "https://github.com/$github_username/$repo_name.git"
    
    # Step 8: Rename branch to main
    print_message "Renaming branch to main..."
    git branch -M main
    
    # Step 9: Push to GitHub
    print_message "Pushing to GitHub..."
    git push -u origin main
    
    print_message "Successfully pushed to GitHub!"
    print_message "Your repository is now available at: https://github.com/$github_username/$repo_name"
else
    print_message "When you're ready to push to GitHub, run the following commands:"
    print_message ""
    print_message "git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPOSITORY_NAME.git"
    print_message "git branch -M main"
    print_message "git push -u origin main"
    print_message ""
    print_warning "Replace YOUR_USERNAME and YOUR_REPOSITORY_NAME with your actual GitHub username and repository name."
fi

# Step 10: Additional information
print_message ""
print_message "Additional GitHub commands you might find useful:"
print_message ""
print_message "# To check the status of your repository"
print_message "git status"
print_message ""
print_message "# To pull changes from GitHub"
print_message "git pull origin main"
print_message ""
print_message "# To create a new branch"
print_message "git checkout -b new-branch-name"
print_message ""
print_message "# To switch to an existing branch"
print_message "git checkout branch-name"
print_message ""
print_message "# To add and commit changes"
print_message "git add ."
print_message "git commit -m \"Your commit message\""
print_message ""
print_message "# To push changes to GitHub"
print_message "git push origin branch-name"