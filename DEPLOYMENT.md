# AWS Deployment Guide for LangGraph Travel Planner

This guide will help you deploy your LangGraph Travel Planner application to AWS using GitHub Actions.

## Architecture Overview

The deployment uses the following AWS services:
- **ECS Fargate**: Containerized FastAPI backend
- **ECR**: Docker image registry
- **ALB**: Application Load Balancer for the backend
- **S3**: Static frontend hosting
- **CloudFront**: CDN for the frontend
- **Secrets Manager**: Secure API key storage
- **CloudWatch**: Logging and monitoring

## Prerequisites

1. **AWS Account**: You need an AWS account with appropriate permissions
2. **GitHub Repository**: Your code should be in a GitHub repository
3. **AWS CLI**: Install and configure AWS CLI locally
4. **Terraform**: Install Terraform for infrastructure setup

## Step 1: AWS Infrastructure Setup

### 1.1 Install Terraform
```bash
# Download and install Terraform from https://terraform.io
# Verify installation
terraform --version
```

### 1.2 Configure AWS Credentials
```bash
aws configure
# Enter your AWS Access Key ID
# Enter your AWS Secret Access Key
# Enter your default region (e.g., us-east-1)
```

### 1.3 Deploy Infrastructure
```bash
cd infrastructure
cp terraform.tfvars.example terraform.tfvars
# Edit terraform.tfvars with your specific values

terraform init
terraform plan
terraform apply
```

### 1.4 Store API Keys in Secrets Manager
```bash
# Store your API keys in AWS Secrets Manager
aws secretsmanager put-secret-value \
  --secret-id "langgraph/groq-api-key" \
  --secret-string "your-groq-api-key"

aws secretsmanager put-secret-value \
  --secret-id "langgraph/tavily-api-key" \
  --secret-string "your-tavily-api-key"

aws secretsmanager put-secret-value \
  --secret-id "langgraph/openai-api-key" \
  --secret-string "your-openai-api-key"
```

## Step 2: GitHub Repository Setup

### 2.1 Create GitHub Secrets
Go to your GitHub repository → Settings → Secrets and variables → Actions, and add the following secrets:

- `AWS_ACCESS_KEY_ID`: Your AWS access key
- `AWS_SECRET_ACCESS_KEY`: Your AWS secret key
- `S3_BUCKET_NAME`: The S3 bucket name from Terraform output
- `CLOUDFRONT_DISTRIBUTION_ID`: The CloudFront distribution ID from Terraform output

### 2.2 Update Task Definition
Edit `.github/aws/task-definition.json` and replace `ACCOUNT_ID` with your actual AWS account ID.

## Step 3: Deploy Application

### 3.1 Push to Main Branch
The GitHub Actions workflow will automatically trigger when you push to the main branch:

```bash
git add .
git commit -m "Initial deployment setup"
git push origin main
```

### 3.2 Monitor Deployment
1. Go to your GitHub repository → Actions tab
2. Monitor the deployment progress
3. Check for any errors in the workflow

## Step 4: Verify Deployment

### 4.1 Backend API
- Get the ALB DNS name from Terraform output
- Test the health endpoint: `http://<alb-dns-name>/health`
- Test the API: `http://<alb-dns-name>/query`

### 4.2 Frontend
- Get the CloudFront domain from Terraform output
- Access your application at the CloudFront URL

## Step 5: Update Frontend Configuration

### 5.1 Update API Endpoint
Edit `streamlitapp.py` and update the `BASE_URL` to point to your ALB:

```python
BASE_URL = "http://your-alb-dns-name/"  # Update this
```

### 5.2 Deploy Frontend Changes
Push the changes to trigger a new deployment:

```bash
git add .
git commit -m "Update frontend API endpoint"
git push origin main
```

## Monitoring and Maintenance

### 5.1 CloudWatch Logs
- Monitor application logs in CloudWatch
- Set up log retention policies
- Create alarms for errors

### 5.2 ECS Service
- Monitor ECS service health
- Set up auto-scaling if needed
- Monitor resource usage

### 5.3 Cost Optimization
- Use Spot instances for cost savings
- Set up billing alerts
- Monitor unused resources

## Troubleshooting

### Common Issues

1. **ECS Task Failing to Start**
   - Check CloudWatch logs
   - Verify environment variables
   - Check security group rules

2. **API Keys Not Working**
   - Verify secrets are stored in Secrets Manager
   - Check IAM permissions for ECS task role
   - Verify secret names in task definition

3. **Frontend Not Loading**
   - Check S3 bucket permissions
   - Verify CloudFront distribution
   - Check CORS settings

4. **GitHub Actions Failing**
   - Verify AWS credentials
   - Check repository secrets
   - Review workflow logs

### Useful Commands

```bash
# Check ECS service status
aws ecs describe-services --cluster langgraph-cluster --services langgraph-service

# View CloudWatch logs
aws logs tail /ecs/langgraph-travel-planner --follow

# Check ALB health
aws elbv2 describe-target-health --target-group-arn <target-group-arn>

# Update ECS service
aws ecs update-service --cluster langgraph-cluster --service langgraph-service --force-new-deployment
```

## Security Best Practices

1. **IAM Roles**: Use least privilege principle
2. **Secrets**: Store all sensitive data in Secrets Manager
3. **Network**: Use private subnets for ECS tasks
4. **HTTPS**: Enable HTTPS for production
5. **Monitoring**: Set up security monitoring and alerts

## Cost Estimation

Estimated monthly costs (us-east-1):
- ECS Fargate: ~$30-50/month
- ALB: ~$20/month
- CloudFront: ~$5-10/month
- S3: ~$1-5/month
- Secrets Manager: ~$1/month
- CloudWatch: ~$5-10/month

**Total: ~$60-100/month**

## Next Steps

1. **Custom Domain**: Set up a custom domain with Route 53
2. **SSL Certificate**: Add HTTPS with ACM
3. **Auto Scaling**: Configure auto-scaling policies
4. **CI/CD Pipeline**: Enhance the deployment pipeline
5. **Monitoring**: Set up comprehensive monitoring and alerting

## Support

For issues or questions:
1. Check the troubleshooting section
2. Review AWS documentation
3. Check GitHub Actions logs
4. Monitor CloudWatch logs and metrics 