#!/bin/bash
# Script para deploy del frontend a S3

set -e

# Variables - ACTUALIZAR CON TUS VALORES
AWS_REGION="us-east-1"
S3_BUCKET="carddemo-frontend-$(date +%s)"  # Nombre único con timestamp

echo "🚀 Iniciando deploy del frontend a S3..."

# 1. Crear bucket S3
echo "📦 Creando bucket S3: ${S3_BUCKET}..."
aws s3 mb s3://${S3_BUCKET} --region ${AWS_REGION}

# 2. Build del frontend
echo "🔨 Construyendo frontend..."
npm run build

# 3. Subir archivos a S3
echo "⬆️  Subiendo archivos a S3..."
aws s3 sync dist/ s3://${S3_BUCKET}/ --delete

# 4. Configurar como sitio web estático
echo "🌐 Configurando sitio web estático..."
aws s3 website s3://${S3_BUCKET}/ \
    --index-document index.html \
    --error-document index.html

# 5. Crear política de bucket para acceso público
echo "🔓 Configurando acceso público..."
cat > /tmp/bucket-policy.json <<EOF
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "PublicReadGetObject",
      "Effect": "Allow",
      "Principal": "*",
      "Action": "s3:GetObject",
      "Resource": "arn:aws:s3:::${S3_BUCKET}/*"
    }
  ]
}
EOF

aws s3api put-bucket-policy \
    --bucket ${S3_BUCKET} \
    --policy file:///tmp/bucket-policy.json

# 6. Deshabilitar bloqueo de acceso público
echo "🔧 Ajustando configuración de acceso..."
aws s3api put-public-access-block \
    --bucket ${S3_BUCKET} \
    --public-access-block-configuration \
    "BlockPublicAcls=false,IgnorePublicAcls=false,BlockPublicPolicy=false,RestrictPublicBuckets=false"

echo "✅ Deploy completado exitosamente!"
echo "🌐 URL del sitio: http://${S3_BUCKET}.s3-website-${AWS_REGION}.amazonaws.com"
echo ""
echo "💡 Próximos pasos:"
echo "   1. Actualizar VITE_API_BASE_URL en .env.production con la URL de API Gateway"
echo "   2. Configurar CloudFront para HTTPS (opcional)"
echo "   3. Configurar dominio personalizado (opcional)"
