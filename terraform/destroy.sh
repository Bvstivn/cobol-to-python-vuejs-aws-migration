#!/bin/bash

# CardDemo Terraform Destroy Script
# This script safely destroys all AWS resources

set -e

# Colors
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m'

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

echo "=================================="
echo "CardDemo Infrastructure Destruction"
echo "=================================="
echo ""

print_warning "This will PERMANENTLY DELETE all AWS resources!"
print_warning "This includes:"
echo "  - RDS Database (all data will be lost)"
echo "  - Lambda Function"
echo "  - S3 Bucket (all frontend files)"
echo "  - CloudFront Distribution"
echo "  - VPC and all networking"
echo "  - ECR Repository (all images)"
echo ""

read -p "Are you sure you want to continue? (type 'yes' to confirm): " CONFIRM

if [ "$CONFIRM" != "yes" ]; then
    echo "Destruction cancelled."
    exit 0
fi

echo ""
print_warning "Last chance! Type 'DELETE' to proceed:"
read -p "> " FINAL_CONFIRM

if [ "$FINAL_CONFIRM" != "DELETE" ]; then
    echo "Destruction cancelled."
    exit 0
fi

echo ""
echo "Destroying infrastructure..."
echo ""

# Empty S3 bucket first (required before deletion)
BUCKET_NAME=$(terraform output -raw frontend_bucket_name 2>/dev/null || echo "")
if [ ! -z "$BUCKET_NAME" ]; then
    echo "Emptying S3 bucket: $BUCKET_NAME"
    aws s3 rm s3://$BUCKET_NAME --recursive || true
fi

# Run terraform destroy
terraform destroy

echo ""
echo "✅ All resources have been destroyed."
echo ""
