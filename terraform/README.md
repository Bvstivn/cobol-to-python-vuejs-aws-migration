# CardDemo Terraform Infrastructure

This Terraform configuration deploys the complete CardDemo application infrastructure on AWS using a serverless architecture.

## 🏗️ Architecture

The infrastructure includes:

- **VPC**: Custom VPC with public and private subnets across 2 AZs
- **RDS PostgreSQL**: Database in private subnets
- **Lambda**: Containerized FastAPI application
- **API Gateway**: HTTP API for backend
- **ECR**: Container registry for Lambda images
- **S3**: Static website hosting for frontend
- **CloudFront**: CDN for global distribution (optional)
- **Secrets Manager**: Secure credential storage
- **CloudWatch**: Logging and monitoring

## 📋 Prerequisites

1. **AWS CLI** installed and configured
   ```bash
   aws configure
   ```

2. **Terraform** installed (>= 1.0)
   ```bash
   terraform version
   ```

3. **Docker** installed (for building Lambda container)
   ```bash
   docker --version
   ```

4. **AWS Account** with appropriate permissions

## 🚀 Quick Start

### 1. Configure Variables

```bash
cd terraform
cp terraform.tfvars.example terraform.tfvars
```

Edit `terraform.tfvars` and set your values:
- `db_password`: Strong database password
- `jwt_secret_key`: Random secret key for JWT
- `aws_region`: Your preferred AWS region
- Other optional configurations

### 2. Initialize Terraform

```bash
terraform init
```

### 3. Review the Plan

```bash
terraform plan
```

### 4. Deploy Infrastructure

```bash
terraform apply
```

Type `yes` when prompted to confirm.

⏱️ **Deployment time**: ~10-15 minutes (RDS takes the longest)

### 5. Deploy Application Code

After infrastructure is created, follow the "Next Steps" output from Terraform:

#### Backend (Lambda)

```bash
# Get ECR repository URL from Terraform output
ECR_URL=$(terraform output -raw ecr_repository_url)

# Login to ECR
aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin $ECR_URL

# Build and push Docker image
cd ../carddemo-api
docker build -t $ECR_URL:latest -f Dockerfile.lambda .
docker push $ECR_URL:latest

# Update Lambda function
FUNCTION_NAME=$(terraform output -raw lambda_function_name)
aws lambda update-function-code --function-name $FUNCTION_NAME --image-uri $ECR_URL:latest
```

#### Frontend (S3 + CloudFront)

```bash
# Get S3 bucket name from Terraform output
BUCKET_NAME=$(terraform output -raw frontend_bucket_name)

# Build frontend
cd ../carddemo-frontend
npm install
npm run build

# Deploy to S3
aws s3 sync dist/ s3://$BUCKET_NAME/ --delete

# Invalidate CloudFront cache (if enabled)
DISTRIBUTION_ID=$(terraform output -raw cloudfront_distribution_id)
aws cloudfront create-invalidation --distribution-id $DISTRIBUTION_ID --paths "/*"
```

### 6. Initialize Database

Connect to the RDS database and run initialization:

```bash
# Get database endpoint
DB_ENDPOINT=$(terraform output -raw database_endpoint)

# Connect using psql (install if needed)
psql -h $DB_ENDPOINT -U carddemo_admin -d carddemo

# Run your database initialization scripts
```

### 7. Access Your Application

```bash
# Get URLs
terraform output deployment_summary
```

- **API**: Check `api_url` from output
- **Frontend**: Check `frontend_url` from output

## 📁 File Structure

```
terraform/
├── main.tf                 # Main configuration and providers
├── variables.tf            # Input variables
├── outputs.tf              # Output values
├── vpc.tf                  # VPC and networking
├── rds.tf                  # RDS PostgreSQL database
├── ecr.tf                  # ECR container registry
├── lambda.tf               # Lambda function
├── api-gateway.tf          # API Gateway configuration
├── s3-frontend.tf          # S3 bucket for frontend
├── cloudfront.tf           # CloudFront distribution
├── terraform.tfvars.example # Example variables file
└── README.md               # This file
```

## 🔧 Configuration Options

### Environment

Set `environment` variable to:
- `dev`: Development (lower retention, skip final snapshots)
- `staging`: Staging environment
- `prod`: Production (longer retention, final snapshots)

### Lambda Configuration

```hcl
lambda_memory_size = 512  # MB (128-10240)
lambda_timeout     = 30   # seconds (1-900)
```

### CloudFront

Enable/disable CloudFront CDN:

```hcl
enable_cloudfront = true  # or false
```

### Custom Domain

To use a custom domain:

1. Create ACM certificate in `us-east-1` (for CloudFront)
2. Set variables:
   ```hcl
   domain_name     = "app.yourdomain.com"
   certificate_arn = "arn:aws:acm:us-east-1:..."
   ```
3. Update DNS to point to CloudFront distribution

### CORS Configuration

```hcl
allowed_origins = ["https://yourdomain.com", "https://www.yourdomain.com"]
```

## 💰 Cost Estimation

For low-medium usage (~1M requests/month):

| Service | Configuration | Monthly Cost |
|---------|--------------|--------------|
| Lambda | 512MB, 1M requests | $5-10 |
| API Gateway | 1M requests | $3.50 |
| RDS | db.t3.micro | $15 |
| S3 | 10GB storage | $0.23 |
| CloudFront | 10GB transfer | $1 |
| **Total** | | **~$25-30** |

*Costs may vary by region and usage. First year may be lower with AWS Free Tier.*

## 🔒 Security Best Practices

1. **Secrets**: Never commit `terraform.tfvars` with real credentials
2. **State**: Use remote state (S3 + DynamoDB) for production
3. **IAM**: Follow principle of least privilege
4. **Encryption**: All data encrypted at rest and in transit
5. **VPC**: Database in private subnets only
6. **CORS**: Restrict origins in production

## 🔄 Updates and Maintenance

### Update Infrastructure

```bash
# Make changes to .tf files
terraform plan
terraform apply
```

### Update Application Code

```bash
# Backend
docker build -t $ECR_URL:latest -f Dockerfile.lambda .
docker push $ECR_URL:latest
aws lambda update-function-code --function-name $FUNCTION_NAME --image-uri $ECR_URL:latest

# Frontend
npm run build
aws s3 sync dist/ s3://$BUCKET_NAME/ --delete
aws cloudfront create-invalidation --distribution-id $DISTRIBUTION_ID --paths "/*"
```

### Destroy Infrastructure

⚠️ **Warning**: This will delete all resources!

```bash
terraform destroy
```

## 📊 Monitoring

### CloudWatch Logs

- Lambda logs: `/aws/lambda/carddemo-{env}-api`
- API Gateway logs: `/aws/apigateway/carddemo-{env}`

### Metrics

View metrics in CloudWatch:
- Lambda invocations, errors, duration
- API Gateway requests, latency, errors
- RDS connections, CPU, storage

## 🐛 Troubleshooting

### Lambda can't connect to RDS

- Check security groups allow traffic
- Verify Lambda is in correct VPC/subnets
- Check RDS endpoint in environment variables

### Frontend not loading

- Check S3 bucket policy allows CloudFront
- Verify CloudFront distribution is deployed
- Check CORS configuration

### API Gateway 502 errors

- Check Lambda function logs
- Verify Lambda has correct IAM permissions
- Check Lambda timeout settings

## 📚 Additional Resources

- [Terraform AWS Provider](https://registry.terraform.io/providers/hashicorp/aws/latest/docs)
- [AWS Lambda Container Images](https://docs.aws.amazon.com/lambda/latest/dg/images-create.html)
- [API Gateway HTTP APIs](https://docs.aws.amazon.com/apigateway/latest/developerguide/http-api.html)
- [CloudFront with S3](https://docs.aws.amazon.com/AmazonCloudFront/latest/DeveloperGuide/GettingStarted.SimpleDistribution.html)

## 🤝 Contributing

Improvements to the Terraform configuration are welcome! Please test thoroughly before submitting changes.

## 📝 License

Apache 2.0 - See LICENSE file for details
