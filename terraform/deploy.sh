#!/bin/bash

# CardDemo Terraform Deployment Script
# This script automates the complete deployment process

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Functions
print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

print_info() {
    echo -e "${YELLOW}ℹ️  $1${NC}"
}

print_header() {
    echo ""
    echo "=================================="
    echo "$1"
    echo "=================================="
    echo ""
}

# Check prerequisites
check_prerequisites() {
    print_header "Checking Prerequisites"
    
    # Check AWS CLI
    if ! command -v aws &> /dev/null; then
        print_error "AWS CLI not found. Please install it first."
        exit 1
    fi
    print_success "AWS CLI found"
    
    # Check Terraform
    if ! command -v terraform &> /dev/null; then
        print_error "Terraform not found. Please install it first."
        exit 1
    fi
    print_success "Terraform found"
    
    # Check Docker
    if ! command -v docker &> /dev/null; then
        print_error "Docker not found. Please install it first."
        exit 1
    fi
    print_success "Docker found"
    
    # Check terraform.tfvars exists
    if [ ! -f "terraform.tfvars" ]; then
        print_error "terraform.tfvars not found. Please create it from terraform.tfvars.example"
        exit 1
    fi
    print_success "terraform.tfvars found"
}

# Deploy infrastructure
deploy_infrastructure() {
    print_header "Deploying Infrastructure with Terraform"
    
    print_info "Initializing Terraform..."
    terraform init
    
    print_info "Planning deployment..."
    terraform plan -out=tfplan
    
    print_info "Applying infrastructure changes..."
    terraform apply tfplan
    
    rm tfplan
    print_success "Infrastructure deployed successfully"
}

# Build and push backend
deploy_backend() {
    print_header "Deploying Backend (Lambda)"
    
    # Get ECR URL from Terraform
    ECR_URL=$(terraform output -raw ecr_repository_url)
    FUNCTION_NAME=$(terraform output -raw lambda_function_name)
    AWS_REGION=$(terraform output -json deployment_summary | jq -r '.region')
    
    print_info "ECR Repository: $ECR_URL"
    print_info "Lambda Function: $FUNCTION_NAME"
    
    # Login to ECR
    print_info "Logging in to ECR..."
    aws ecr get-login-password --region $AWS_REGION | docker login --username AWS --password-stdin $ECR_URL
    
    # Build Docker image
    print_info "Building Docker image..."
    cd ../carddemo-api
    docker build -t $ECR_URL:latest -f Dockerfile.lambda .
    
    # Push to ECR
    print_info "Pushing image to ECR..."
    docker push $ECR_URL:latest
    
    # Update Lambda function
    print_info "Updating Lambda function..."
    aws lambda update-function-code \
        --function-name $FUNCTION_NAME \
        --image-uri $ECR_URL:latest \
        --region $AWS_REGION
    
    # Wait for Lambda to be updated
    print_info "Waiting for Lambda update to complete..."
    aws lambda wait function-updated \
        --function-name $FUNCTION_NAME \
        --region $AWS_REGION
    
    cd ../terraform
    print_success "Backend deployed successfully"
}

# Build and deploy frontend
deploy_frontend() {
    print_header "Deploying Frontend (S3 + CloudFront)"
    
    # Get S3 bucket and CloudFront from Terraform
    BUCKET_NAME=$(terraform output -raw frontend_bucket_name)
    CLOUDFRONT_ID=$(terraform output -raw cloudfront_distribution_id)
    AWS_REGION=$(terraform output -json deployment_summary | jq -r '.region')
    
    print_info "S3 Bucket: $BUCKET_NAME"
    
    # Build frontend
    print_info "Building frontend..."
    cd ../carddemo-frontend
    npm install
    npm run build
    
    # Deploy to S3
    print_info "Uploading to S3..."
    aws s3 sync dist/ s3://$BUCKET_NAME/ --delete --region $AWS_REGION
    
    # Invalidate CloudFront cache if enabled
    if [ "$CLOUDFRONT_ID" != "N/A" ]; then
        print_info "Invalidating CloudFront cache..."
        aws cloudfront create-invalidation \
            --distribution-id $CLOUDFRONT_ID \
            --paths "/*"
    fi
    
    cd ../terraform
    print_success "Frontend deployed successfully"
}

# Display deployment summary
show_summary() {
    print_header "Deployment Summary"
    
    terraform output deployment_summary
    
    echo ""
    print_success "Deployment completed successfully!"
    echo ""
    print_info "Next steps:"
    echo "1. Initialize the database with sample data"
    echo "2. Test the API endpoint"
    echo "3. Access the frontend URL"
    echo ""
}

# Main deployment flow
main() {
    print_header "CardDemo AWS Deployment"
    
    # Parse arguments
    SKIP_INFRA=false
    SKIP_BACKEND=false
    SKIP_FRONTEND=false
    
    while [[ $# -gt 0 ]]; do
        case $1 in
            --skip-infra)
                SKIP_INFRA=true
                shift
                ;;
            --skip-backend)
                SKIP_BACKEND=true
                shift
                ;;
            --skip-frontend)
                SKIP_FRONTEND=true
                shift
                ;;
            --help)
                echo "Usage: ./deploy.sh [OPTIONS]"
                echo ""
                echo "Options:"
                echo "  --skip-infra     Skip infrastructure deployment"
                echo "  --skip-backend   Skip backend deployment"
                echo "  --skip-frontend  Skip frontend deployment"
                echo "  --help           Show this help message"
                exit 0
                ;;
            *)
                print_error "Unknown option: $1"
                echo "Use --help for usage information"
                exit 1
                ;;
        esac
    done
    
    # Run deployment steps
    check_prerequisites
    
    if [ "$SKIP_INFRA" = false ]; then
        deploy_infrastructure
    else
        print_info "Skipping infrastructure deployment"
    fi
    
    if [ "$SKIP_BACKEND" = false ]; then
        deploy_backend
    else
        print_info "Skipping backend deployment"
    fi
    
    if [ "$SKIP_FRONTEND" = false ]; then
        deploy_frontend
    else
        print_info "Skipping frontend deployment"
    fi
    
    show_summary
}

# Run main function
main "$@"
