# AWS Setup Script for LangGraph Travel Planner (Windows PowerShell)
# This script helps set up the initial AWS configuration on Windows

param(
    [string]$Region = "us-east-1"
)

Write-Host "🚀 Setting up AWS infrastructure for LangGraph Travel Planner..." -ForegroundColor Green

# Function to print colored output
function Write-Status {
    param([string]$Message)
    Write-Host "[INFO] $Message" -ForegroundColor Green
}

function Write-Warning {
    param([string]$Message)
    Write-Host "[WARNING] $Message" -ForegroundColor Yellow
}

function Write-Error {
    param([string]$Message)
    Write-Host "[ERROR] $Message" -ForegroundColor Red
}

# Check if AWS CLI is installed
try {
    $null = Get-Command aws -ErrorAction Stop
    Write-Status "AWS CLI is installed"
} catch {
    Write-Error "AWS CLI is not installed. Please install it first from https://aws.amazon.com/cli/"
    exit 1
}

# Check if Terraform is installed
try {
    $null = Get-Command terraform -ErrorAction Stop
    Write-Status "Terraform is installed"
} catch {
    Write-Error "Terraform is not installed. Please install it first from https://terraform.io"
    exit 1
}

# Check if AWS credentials are configured
try {
    $callerIdentity = aws sts get-caller-identity 2>$null
    if ($LASTEXITCODE -ne 0) {
        throw "AWS credentials not configured"
    }
    Write-Status "AWS credentials are configured"
} catch {
    Write-Error "AWS credentials are not configured. Please run 'aws configure' first."
    exit 1
}

# Get AWS account ID
$accountId = (aws sts get-caller-identity --query Account --output text 2>$null).Trim()
Write-Status "AWS Account ID: $accountId"

# Create terraform.tfvars if it doesn't exist
if (-not (Test-Path "infrastructure/terraform.tfvars")) {
    Write-Status "Creating terraform.tfvars file..."
    Copy-Item "infrastructure/terraform.tfvars.example" "infrastructure/terraform.tfvars"
    Write-Warning "Please edit infrastructure/terraform.tfvars with your specific values."
} else {
    Write-Status "terraform.tfvars already exists."
}

# Update task definition with account ID
Write-Status "Updating task definition with your AWS account ID..."
$taskDefContent = Get-Content ".github/aws/task-definition.json" -Raw
$taskDefContent = $taskDefContent -replace "ACCOUNT_ID", $accountId
Set-Content ".github/aws/task-definition.json" $taskDefContent

# Initialize Terraform
Write-Status "Initializing Terraform..."
Set-Location infrastructure
terraform init

# Plan Terraform deployment
Write-Status "Planning Terraform deployment..."
terraform plan

Write-Status "Setup complete! Next steps:"
Write-Host ""
Write-Host "1. Review the Terraform plan above" -ForegroundColor Cyan
Write-Host "2. Edit infrastructure/terraform.tfvars if needed" -ForegroundColor Cyan
Write-Host "3. Run: terraform apply" -ForegroundColor Cyan
Write-Host "4. Store your API keys in AWS Secrets Manager:" -ForegroundColor Cyan
Write-Host "   - langgraph/groq-api-key" -ForegroundColor Yellow
Write-Host "   - langgraph/tavily-api-key" -ForegroundColor Yellow
Write-Host "   - langgraph/openai-api-key" -ForegroundColor Yellow
Write-Host "5. Add GitHub secrets to your repository" -ForegroundColor Cyan
Write-Host "6. Push to main branch to trigger deployment" -ForegroundColor Cyan
Write-Host ""
Write-Host "For detailed instructions, see DEPLOYMENT.md" -ForegroundColor Green

# Return to original directory
Set-Location .. 