# 🚀 Guía de Migración a AWS - CardDemo Application

## 📋 Resumen

Esta guía proporciona el paso a paso completo y todo el código necesario para migrar la aplicación CardDemo a AWS usando una arquitectura serverless.

**Arquitectura:**
- **Frontend (Vue.js)**: AWS Amplify Hosting o S3 + CloudFront
- **Backend (FastAPI)**: AWS Lambda + API Gateway
- **Base de Datos**: Amazon RDS (PostgreSQL) o DynamoDB

---

## 🎯 Opción 1: Serverless con AWS Lambda (Recomendada)

### Parte 1: Preparar el Backend para Lambda

#### 1.1 Crear Dockerfile para Lambda

Crear archivo `carddemo-api/Dockerfile`:

```dockerfile
# Usar imagen base de AWS Lambda para Python 3.13
FROM public.ecr.aws/lambda/python:3.13

# Copiar requirements
COPY requirements.txt ${LAMBDA_TASK_ROOT}/

# Instalar dependencias
RUN pip install --no-cache-dir -r requirements.txt

# Copiar código de la aplicación
COPY . ${LAMBDA_TASK_ROOT}/

# Instalar Mangum para adaptar FastAPI a Lambda
RUN pip install mangum

# Crear handler para Lambda
CMD ["lambda_handler.handler"]
```

#### 1.2 Crear Lambda Handler

Crear archivo `carddemo-api/lambda_handler.py`:

```python
"""
Lambda Handler para FastAPI con Mangum
"""
from mangum import Mangum
from main import app

# Mangum adapta FastAPI para AWS Lambda
handler = Mangum(app, lifespan="off")
```

#### 1.3 Actualizar requirements.txt

Agregar a `carddemo-api/requirements.txt`:

```txt
mangum==0.17.0
```

#### 1.4 Script de Build y Deploy

Crear archivo `carddemo-api/deploy-lambda.sh`:

```bash
#!/bin/bash

# Variables
AWS_REGION="us-east-1"
AWS_ACCOUNT_ID="YOUR_ACCOUNT_ID"
ECR_REPO_NAME="carddemo-api"
LAMBDA_FUNCTION_NAME="carddemo-api"

# 1. Crear repositorio ECR (solo primera vez)
aws ecr create-repository \
    --repository-name ${ECR_REPO_NAME} \
    --region ${AWS_REGION}

# 2. Autenticar Docker con ECR
aws ecr get-login-password --region ${AWS_REGION} | \
    docker login --username AWS --password-stdin \
    ${AWS_ACCOUNT_ID}.dkr.ecr.${AWS_REGION}.amazonaws.com

# 3. Build de la imagen Docker
docker build --platform linux/amd64 -t ${ECR_REPO_NAME}:latest .

# 4. Tag de la imagen
docker tag ${ECR_REPO_NAME}:latest \
    ${AWS_ACCOUNT_ID}.dkr.ecr.${AWS_REGION}.amazonaws.com/${ECR_REPO_NAME}:latest

# 5. Push a ECR
docker push ${AWS_ACCOUNT_ID}.dkr.ecr.${AWS_REGION}.amazonaws.com/${ECR_REPO_NAME}:latest

# 6. Crear o actualizar función Lambda
aws lambda update-function-code \
    --function-name ${LAMBDA_FUNCTION_NAME} \
    --image-uri ${AWS_ACCOUNT_ID}.dkr.ecr.${AWS_REGION}.amazonaws.com/${ECR_REPO_NAME}:latest \
    --region ${AWS_REGION}

echo "✅ Deploy completado!"
```

#### 1.5 Crear función Lambda (primera vez)

Crear archivo `carddemo-api/create-lambda.sh`:

```bash
#!/bin/bash

AWS_REGION="us-east-1"
AWS_ACCOUNT_ID="YOUR_ACCOUNT_ID"
ECR_REPO_NAME="carddemo-api"
LAMBDA_FUNCTION_NAME="carddemo-api"
LAMBDA_ROLE_ARN="arn:aws:iam::${AWS_ACCOUNT_ID}:role/lambda-execution-role"

# Crear función Lambda
aws lambda create-function \
    --function-name ${LAMBDA_FUNCTION_NAME} \
    --package-type Image \
    --code ImageUri=${AWS_ACCOUNT_ID}.dkr.ecr.${AWS_REGION}.amazonaws.com/${ECR_REPO_NAME}:latest \
    --role ${LAMBDA_ROLE_ARN} \
    --timeout 30 \
    --memory-size 512 \
    --environment Variables="{
        DATABASE_URL=postgresql://user:pass@rds-endpoint:5432/carddemo,
        SECRET_KEY=your-secret-key,
        DEBUG=False
    }" \
    --region ${AWS_REGION}
```

---

### Parte 2: Configurar API Gateway

#### 2.1 Crear API Gateway REST API

```bash
#!/bin/bash

AWS_REGION="us-east-1"
LAMBDA_FUNCTION_NAME="carddemo-api"

# Crear API
API_ID=$(aws apigatewayv2 create-api \
    --name "CardDemo API" \
    --protocol-type HTTP \
    --target arn:aws:lambda:${AWS_REGION}:${AWS_ACCOUNT_ID}:function:${LAMBDA_FUNCTION_NAME} \
    --region ${AWS_REGION} \
    --query 'ApiId' \
    --output text)

echo "API Gateway creado: ${API_ID}"
echo "URL: https://${API_ID}.execute-api.${AWS_REGION}.amazonaws.com"
```

#### 2.2 Configurar CORS en API Gateway

Crear archivo `carddemo-api/api-gateway-cors.json`:

```json
{
  "CorsConfiguration": {
    "AllowOrigins": ["*"],
    "AllowMethods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    "AllowHeaders": ["Content-Type", "Authorization"],
    "MaxAge": 300
  }
}
```

Aplicar configuración:

```bash
aws apigatewayv2 update-api \
    --api-id ${API_ID} \
    --cors-configuration file://api-gateway-cors.json \
    --region ${AWS_REGION}
```

---

### Parte 3: Configurar Base de Datos RDS

#### 3.1 Crear RDS PostgreSQL

```bash
#!/bin/bash

AWS_REGION="us-east-1"
DB_INSTANCE_ID="carddemo-db"
DB_NAME="carddemo"
DB_USERNAME="admin"
DB_PASSWORD="YourSecurePassword123!"

# Crear instancia RDS
aws rds create-db-instance \
    --db-instance-identifier ${DB_INSTANCE_ID} \
    --db-instance-class db.t3.micro \
    --engine postgres \
    --engine-version 15.4 \
    --master-username ${DB_USERNAME} \
    --master-user-password ${DB_PASSWORD} \
    --allocated-storage 20 \
    --db-name ${DB_NAME} \
    --backup-retention-period 7 \
    --publicly-accessible \
    --region ${AWS_REGION}

echo "⏳ Esperando que RDS esté disponible..."
aws rds wait db-instance-available \
    --db-instance-identifier ${DB_INSTANCE_ID} \
    --region ${AWS_REGION}

# Obtener endpoint
DB_ENDPOINT=$(aws rds describe-db-instances \
    --db-instance-identifier ${DB_INSTANCE_ID} \
    --query 'DBInstances[0].Endpoint.Address' \
    --output text \
    --region ${AWS_REGION})

echo "✅ RDS creado!"
echo "Endpoint: ${DB_ENDPOINT}"
echo "Connection String: postgresql://${DB_USERNAME}:${DB_PASSWORD}@${DB_ENDPOINT}:5432/${DB_NAME}"
```

#### 3.2 Actualizar código para PostgreSQL

Modificar `carddemo-api/config.py`:

```python
import os
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # Base de datos - usar PostgreSQL en AWS
    database_url: str = os.getenv(
        "DATABASE_URL",
        "postgresql://admin:password@localhost:5432/carddemo"
    )
    
    # ... resto de configuración
```

Actualizar `requirements.txt`:

```txt
psycopg2-binary==2.9.9  # Driver PostgreSQL
```

---

### Parte 4: Deploy del Frontend a AWS Amplify

#### 4.1 Preparar el Frontend

Crear archivo `carddemo-frontend/amplify.yml`:

```yaml
version: 1
frontend:
  phases:
    preBuild:
      commands:
        - npm ci
    build:
      commands:
        - npm run build
  artifacts:
    baseDirectory: dist
    files:
      - '**/*'
  cache:
    paths:
      - node_modules/**/*
```

#### 4.2 Actualizar variables de entorno

Crear `carddemo-frontend/.env.production`:

```env
VITE_API_BASE_URL=https://YOUR_API_ID.execute-api.us-east-1.amazonaws.com
VITE_APP_TITLE=CardDemo
VITE_APP_VERSION=1.0.0
```

#### 4.3 Deploy con Amplify CLI

```bash
# Instalar Amplify CLI
npm install -g @aws-amplify/cli

# Configurar Amplify
amplify configure

# Inicializar proyecto
cd carddemo-frontend
amplify init

# Agregar hosting
amplify add hosting

# Seleccionar:
# - Hosting with Amplify Console
# - Manual deployment

# Deploy
amplify publish
```

#### 4.4 Deploy manual desde S3

Alternativa más simple:

```bash
#!/bin/bash

AWS_REGION="us-east-1"
S3_BUCKET="carddemo-frontend"

# 1. Crear bucket S3
aws s3 mb s3://${S3_BUCKET} --region ${AWS_REGION}

# 2. Build del frontend
cd carddemo-frontend
npm run build

# 3. Subir a S3
aws s3 sync dist/ s3://${S3_BUCKET}/ --delete

# 4. Configurar como sitio web
aws s3 website s3://${S3_BUCKET}/ \
    --index-document index.html \
    --error-document index.html

# 5. Hacer público
aws s3api put-bucket-policy \
    --bucket ${S3_BUCKET} \
    --policy file://bucket-policy.json

echo "✅ Frontend desplegado!"
echo "URL: http://${S3_BUCKET}.s3-website-${AWS_REGION}.amazonaws.com"
```

Crear `bucket-policy.json`:

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "PublicReadGetObject",
      "Effect": "Allow",
      "Principal": "*",
      "Action": "s3:GetObject",
      "Resource": "arn:aws:s3:::carddemo-frontend/*"
    }
  ]
}
```

---

### Parte 5: Configurar CloudFront (CDN)

#### 5.1 Crear distribución CloudFront

```bash
#!/bin/bash

S3_BUCKET="carddemo-frontend"
AWS_REGION="us-east-1"

# Crear distribución
aws cloudfront create-distribution \
    --origin-domain-name ${S3_BUCKET}.s3.${AWS_REGION}.amazonaws.com \
    --default-root-object index.html \
    --query 'Distribution.DomainName' \
    --output text

echo "✅ CloudFront configurado!"
```

Crear archivo `cloudfront-config.json`:

```json
{
  "CallerReference": "carddemo-frontend-2024",
  "Comment": "CardDemo Frontend Distribution",
  "Enabled": true,
  "Origins": {
    "Quantity": 1,
    "Items": [
      {
        "Id": "S3-carddemo-frontend",
        "DomainName": "carddemo-frontend.s3.us-east-1.amazonaws.com",
        "S3OriginConfig": {
          "OriginAccessIdentity": ""
        }
      }
    ]
  },
  "DefaultCacheBehavior": {
    "TargetOriginId": "S3-carddemo-frontend",
    "ViewerProtocolPolicy": "redirect-to-https",
    "AllowedMethods": {
      "Quantity": 2,
      "Items": ["GET", "HEAD"]
    },
    "ForwardedValues": {
      "QueryString": false,
      "Cookies": {
        "Forward": "none"
      }
    },
    "MinTTL": 0
  }
}
```

---

## 📦 Estructura de Archivos Necesarios

```
carddemo-api/
├── Dockerfile                 # Imagen Docker para Lambda
├── lambda_handler.py          # Handler de Lambda
├── deploy-lambda.sh          # Script de deploy
├── create-lambda.sh          # Script de creación inicial
├── api-gateway-cors.json     # Configuración CORS
└── requirements.txt          # Dependencias (agregar mangum, psycopg2)

carddemo-frontend/
├── amplify.yml               # Configuración Amplify
├── .env.production           # Variables de producción
├── bucket-policy.json        # Política S3
├── cloudfront-config.json    # Configuración CloudFront
└── deploy-s3.sh             # Script de deploy a S3
```

---

## 🔧 Comandos Rápidos

### Backend (Lambda)
```bash
# 1. Build y push a ECR
cd carddemo-api
chmod +x deploy-lambda.sh
./deploy-lambda.sh

# 2. Crear función Lambda (primera vez)
chmod +x create-lambda.sh
./create-lambda.sh
```

### Frontend (S3 + CloudFront)
```bash
# 1. Deploy a S3
cd carddemo-frontend
chmod +x deploy-s3.sh
./deploy-s3.sh

# 2. Configurar CloudFront
aws cloudfront create-distribution --cli-input-json file://cloudfront-config.json
```

---

## 💰 Estimación de Costos (Uso Bajo)

- **Lambda**: ~$5-10/mes (1M requests)
- **API Gateway**: ~$3.50/mes (1M requests)
- **RDS t3.micro**: ~$15/mes
- **S3**: ~$1/mes (5GB storage)
- **CloudFront**: ~$1/mes (10GB transfer)

**Total estimado**: ~$25-30/mes

---

## ✅ Checklist de Migración

### Pre-requisitos
- [ ] Cuenta AWS configurada
- [ ] AWS CLI instalado y configurado
- [ ] Docker instalado
- [ ] Permisos IAM necesarios

### Backend
- [ ] Dockerfile creado
- [ ] Lambda handler creado
- [ ] Repositorio ECR creado
- [ ] Imagen Docker pusheada a ECR
- [ ] Función Lambda creada
- [ ] API Gateway configurado
- [ ] RDS PostgreSQL creado
- [ ] Variables de entorno configuradas

### Frontend
- [ ] Build de producción funciona
- [ ] Variables de entorno actualizadas
- [ ] Bucket S3 creado
- [ ] Archivos subidos a S3
- [ ] CloudFront configurado
- [ ] DNS configurado (opcional)

### Testing
- [ ] API responde correctamente
- [ ] Frontend carga correctamente
- [ ] Login funciona
- [ ] CORS configurado correctamente
- [ ] Base de datos conectada

---

## 🔍 Troubleshooting

### Error: Lambda timeout
```bash
# Aumentar timeout
aws lambda update-function-configuration \
    --function-name carddemo-api \
    --timeout 60
```

### Error: CORS
```bash
# Verificar configuración API Gateway
aws apigatewayv2 get-api --api-id YOUR_API_ID
```

### Error: Base de datos
```bash
# Verificar security group permite conexiones desde Lambda
# Agregar Lambda VPC a security group de RDS
```

---

## 📚 Referencias

- [AWS Lambda Python](https://docs.aws.amazon.com/lambda/latest/dg/python-image.html)
- [AWS Amplify Hosting](https://docs.aws.amazon.com/amplify/latest/userguide/deploy-website-from-s3.html)
- [API Gateway](https://docs.aws.amazon.com/apigateway/)
- [Amazon RDS](https://docs.aws.amazon.com/rds/)
- [Mangum (FastAPI + Lambda)](https://mangum.io/)

---

**Nota**: Esta es una guía para prueba de concepto. Para producción, considera:
- Usar AWS Secrets Manager para credenciales
- Configurar WAF para seguridad
- Implementar CI/CD con CodePipeline
- Configurar monitoreo con CloudWatch
- Usar Route 53 para DNS personalizado
