#!/bin/bash

# AWS Setup Script for LangGraph Travel Planner
# This script helps set up the initial AWS configuration

set -e

echo "🚀 Setting up AWS infrastructure for LangGraph Travel Planner..."

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
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

# Check if Terraform is installed
if ! command -v terraform &> /dev/null; then
    print_error "Terraform is not installed. Please install it first."
    exit 1
fi

# Check if AWS credentials are configured
if ! aws sts get-caller-identity &> /dev/null; then
    print_error "AWS credentials are not configured. Please run 'aws configure' first."
    exit 1
fi

print_status "AWS CLI and Terraform are properly configured."

# Get AWS account ID
ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)
print_status "AWS Account ID: $ACCOUNT_ID"

# Create terraform.tfvars if it doesn't exist
if [ ! -f "infrastructure/terraform.tfvars" ]; then
    print_status "Creating terraform.tfvars file..."
    cp infrastructure/terraform.tfvars.example infrastructure/terraform.tfvars
    print_warning "Please edit infrastructure/terraform.tfvars with your specific values."
else
    print_status "terraform.tfvars already exists."
fi

# Update task definition with account ID
print_status "Updating task definition with your AWS account ID..."
sed -i "s/ACCOUNT_ID/$ACCOUNT_ID/g" .github/aws/task-definition.json

# Initialize Terraform
print_status "Initializing Terraform..."
cd infrastructure
terraform init

# Plan Terraform deployment
print_status "Planning Terraform deployment..."
terraform plan

print_status "Setup complete! Next steps:"
echo ""
echo "1. Review the Terraform plan above"
echo "2. Edit infrastructure/terraform.tfvars if needed"
echo "3. Run: terraform apply"
echo "4. Store your API keys in AWS Secrets Manager:"
echo "   - langgraph/groq-api-key"
echo "   - langgraph/tavily-api-key"
echo "   - langgraph/openai-api-key"
echo "5. Add GitHub secrets to your repository"
echo "6. Push to main branch to trigger deployment"
echo ""
echo "For detailed instructions, see DEPLOYMENT.md" 