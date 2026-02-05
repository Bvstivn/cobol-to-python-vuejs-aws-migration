#!/bin/bash
# Script para deploy del backend a AWS Lambda

set -e

# Variables - ACTUALIZAR CON TUS VALORES
AWS_REGION="us-east-1"
AWS_ACCOUNT_ID="YOUR_ACCOUNT_ID"  # Reemplazar con tu Account ID
ECR_REPO_NAME="carddemo-api"
LAMBDA_FUNCTION_NAME="carddemo-api"

echo "🚀 Iniciando deploy a AWS Lambda..."

# 1. Crear repositorio ECR (solo primera vez, ignorar error si ya existe)
echo "📦 Verificando repositorio ECR..."
aws ecr create-repository \
    --repository-name ${ECR_REPO_NAME} \
    --region ${AWS_REGION} 2>/dev/null || echo "Repositorio ya existe"

# 2. Autenticar Docker con ECR
echo "🔐 Autenticando Docker con ECR..."
aws ecr get-login-password --region ${AWS_REGION} | \
    docker login --username AWS --password-stdin \
    ${AWS_ACCOUNT_ID}.dkr.ecr.${AWS_REGION}.amazonaws.com

# 3. Build de la imagen Docker
echo "🔨 Construyendo imagen Docker..."
docker build --platform linux/amd64 -f Dockerfile.lambda -t ${ECR_REPO_NAME}:latest .

# 4. Tag de la imagen
echo "🏷️  Etiquetando imagen..."
docker tag ${ECR_REPO_NAME}:latest \
    ${AWS_ACCOUNT_ID}.dkr.ecr.${AWS_REGION}.amazonaws.com/${ECR_REPO_NAME}:latest

# 5. Push a ECR
echo "⬆️  Subiendo imagen a ECR..."
docker push ${AWS_ACCOUNT_ID}.dkr.ecr.${AWS_REGION}.amazonaws.com/${ECR_REPO_NAME}:latest

# 6. Actualizar función Lambda
echo "🔄 Actualizando función Lambda..."
aws lambda update-function-code \
    --function-name ${LAMBDA_FUNCTION_NAME} \
    --image-uri ${AWS_ACCOUNT_ID}.dkr.ecr.${AWS_REGION}.amazonaws.com/${ECR_REPO_NAME}:latest \
    --region ${AWS_REGION}

echo "✅ Deploy completado exitosamente!"
echo "📍 Función Lambda: ${LAMBDA_FUNCTION_NAME}"
echo "🌐 Región: ${AWS_REGION}"
