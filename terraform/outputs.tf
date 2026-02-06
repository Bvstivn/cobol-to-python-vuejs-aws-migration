# Terraform Outputs

output "vpc_id" {
  description = "VPC ID"
  value       = aws_vpc.main.id
}

output "database_endpoint" {
  description = "RDS database endpoint"
  value       = aws_db_instance.main.endpoint
  sensitive   = true
}

output "database_name" {
  description = "Database name"
  value       = aws_db_instance.main.db_name
}

output "lambda_function_name" {
  description = "Lambda function name"
  value       = aws_lambda_function.api.function_name
}

output "lambda_function_arn" {
  description = "Lambda function ARN"
  value       = aws_lambda_function.api.arn
}

output "deployment_summary" {
  description = "Deployment summary with all important URLs and information"
  value = {
    environment         = var.environment
    region              = var.aws_region
    api_url             = aws_apigatewayv2_stage.main.invoke_url
    frontend_url        = var.enable_cloudfront ? "https://${aws_cloudfront_distribution.frontend[0].domain_name}" : "https://${aws_s3_bucket.frontend.bucket_regional_domain_name}"
    ecr_repository      = aws_ecr_repository.lambda.repository_url
    frontend_bucket     = aws_s3_bucket.frontend.id
    lambda_function     = aws_lambda_function.api.function_name
    database_endpoint   = aws_db_instance.main.endpoint
    cloudfront_enabled  = var.enable_cloudfront
  }
}

output "next_steps" {
  description = "Next steps after Terraform deployment"
  value = <<-EOT
    
    ✅ Infrastructure deployed successfully!
    
    Next steps:
    
    1. Build and push Docker image to ECR:
       cd ../carddemo-api
       aws ecr get-login-password --region ${var.aws_region} | docker login --username AWS --password-stdin ${aws_ecr_repository.lambda.repository_url}
       docker build -t ${aws_ecr_repository.lambda.repository_url}:latest -f Dockerfile.lambda .
       docker push ${aws_ecr_repository.lambda.repository_url}:latest
    
    2. Update Lambda function with new image:
       aws lambda update-function-code --function-name ${aws_lambda_function.api.function_name} --image-uri ${aws_ecr_repository.lambda.repository_url}:latest
    
    3. Build and deploy frontend:
       cd ../carddemo-frontend
       npm run build
       aws s3 sync dist/ s3://${aws_s3_bucket.frontend.id}/ --delete
       ${var.enable_cloudfront ? "aws cloudfront create-invalidation --distribution-id ${aws_cloudfront_distribution.frontend[0].id} --paths '/*'" : ""}
    
    4. Initialize database:
       Run the database initialization script against: ${aws_db_instance.main.endpoint}
    
    5. Test your application:
       API: ${aws_apigatewayv2_stage.main.invoke_url}
       Frontend: ${var.enable_cloudfront ? "https://${aws_cloudfront_distribution.frontend[0].domain_name}" : "https://${aws_s3_bucket.frontend.bucket_regional_domain_name}"}
    
  EOT
}
