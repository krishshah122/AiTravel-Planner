variable "aws_region" {
  description = "AWS region"
  type        = string
  default     = "us-east-1"
}

variable "project_name" {
  description = "Name of the project"
  type        = string
  default     = "langgraph-travel-planner"
}

variable "availability_zones" {
  description = "Availability zones"
  type        = list(string)
  default     = ["us-east-1a", "us-east-1b"]
}

variable "ecr_repository_name" {
  description = "Name of the ECR repository"
  type        = string
  default     = "langgraph-travel-planner"
}

variable "ecs_cluster_name" {
  description = "Name of the ECS cluster"
  type        = string
  default     = "langgraph-cluster"
}

variable "s3_bucket_name" {
  description = "Name of the S3 bucket for frontend"
  type        = string
  default     = "langgraph-travel-planner-frontend"
} 