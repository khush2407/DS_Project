#!/bin/bash

# Script to fix the "non-fast-forward" error when pushing to GitHub
# This script provides multiple options to resolve the issue

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

# Check if we're in a Git repository
if ! git rev-parse --is-inside-work-tree &> /dev/null; then
    print_error "Not in a Git repository. Please run this script from within your Git repository."
    exit 1
fi

# Get remote URL
REMOTE_URL=$(git remote get-url origin 2>/dev/null)
if [ -z "$REMOTE_URL" ]; then
    print_error "No remote named 'origin' found. Please set up your remote first."
    exit 1
fi

print_message "Current remote URL: $REMOTE_URL"
print_message ""
print_message "You're encountering a 'non-fast-forward' error because the remote repository"
print_message "already has content that doesn't match your local repository."
print_message ""
print_message "Here are your options to resolve this issue:"
print_message ""
print_message "1. Pull remote changes, then push (recommended if you want to keep remote content)"
print_message "2. Force push your local changes (WARNING: this will overwrite remote content)"
print_message "3. Create a new branch and push that instead"
print_message "4. Show remote branches and their commits"
print_message "5. Exit without making changes"
print_message ""

read -p "Enter your choice (1-5): " choice

case $choice in
    1)
        print_message "Pulling remote changes and then pushing..."
        print_message "This may result in merge conflicts that you'll need to resolve manually."
        print_warning "If you have uncommitted changes, they might be overwritten."
        read -p "Do you want to continue? (y/n): " confirm
        if [ "$confirm" = "y" ]; then
            # Stash any uncommitted changes
            git stash
            
            # Pull with rebase to avoid a merge commit
            git pull --rebase origin main
            
            # Check for conflicts
            if [ $? -ne 0 ]; then
                print_error "There were conflicts during the pull. Please resolve them manually."
                print_message "After resolving conflicts, run:"
                print_message "git rebase --continue"
                print_message "git push origin main"
                exit 1
            fi
            
            # Push changes
            git push origin main
            
            # Pop stashed changes if any
            git stash pop
            
            print_message "Successfully pulled remote changes and pushed your local changes."
        else
            print_message "Operation cancelled."
        fi
        ;;
    2)
        print_warning "WARNING: Force pushing will overwrite the remote repository with your local changes."
        print_warning "Any changes in the remote repository that are not in your local repository will be lost."
        read -p "Are you sure you want to force push? (y/n): " confirm
        if [ "$confirm" = "y" ]; then
            git push --force origin main
            print_message "Successfully force pushed your local changes."
        else
            print_message "Operation cancelled."
        fi
        ;;
    3)
        read -p "Enter a name for the new branch: " branch_name
        if [ -z "$branch_name" ]; then
            branch_name="feature-$(date +%Y%m%d%H%M%S)"
            print_message "Using generated branch name: $branch_name"
        fi
        
        # Create and switch to the new branch
        git checkout -b $branch_name
        
        # Push the new branch
        git push -u origin $branch_name
        
        print_message "Successfully created and pushed branch: $branch_name"
        print_message "You can now create a pull request on GitHub to merge your changes into main."
        ;;
    4)
        print_message "Fetching remote branches..."
        git fetch
        
        print_message "\nRemote branches:"
        git branch -r
        
        print_message "\nRemote main branch commits:"
        git log --oneline origin/main -n 5
        
        print_message "\nLocal main branch commits:"
        git log --oneline main -n 5
        
        print_message "\nTo see differences between local and remote:"
        print_message "git diff main origin/main"
        ;;
    5)
        print_message "Exiting without making changes."
        ;;
    *)
        print_error "Invalid choice. Exiting."
        ;;
esac

print_message ""
print_message "Additional helpful Git commands:"
print_message ""
print_message "# To see the status of your repository"
print_message "git status"
print_message ""
print_message "# To see the differences between your local and remote repository"
print_message "git diff main origin/main"
print_message ""
print_message "# To reset your local repository to match the remote repository"
print_message "git fetch origin"
print_message "git reset --hard origin/main"
print_message ""
print_message "# To create a new repository from scratch"
print_message "1. Delete the .git directory: rm -rf .git"
print_message "2. Initialize a new repository: git init"
print_message "3. Add all files: git add ."
print_message "4. Commit: git commit -m \"Initial commit\""
print_message "5. Add remote: git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPOSITORY_NAME.git"
print_message "6. Push: git push -u origin main"