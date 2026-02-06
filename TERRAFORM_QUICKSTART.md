# 🚀 Terraform Quick Start Guide

Despliegue completo de CardDemo en AWS con un solo comando usando Terraform.

## ⚡ Despliegue Rápido (5 minutos)

### 1. Configurar credenciales

```bash
cd terraform
cp terraform.tfvars.example terraform.tfvars
```

Edita `terraform.tfvars` y configura:

```hcl
aws_region  = "us-east-1"
environment = "dev"

# Credenciales de base de datos
db_username = "carddemo_admin"
db_password = "TuPasswordSeguro123!"  # ⚠️ Usa un password fuerte

# JWT Secret (genera uno aleatorio)
jwt_secret_key = "tu-secret-key-aleatorio-muy-largo"

# CORS (en producción, especifica dominios exactos)
allowed_origins = ["*"]
```

### 2. Desplegar todo

```bash
chmod +x deploy.sh
./deploy.sh
```

⏱️ **Tiempo estimado**: 10-15 minutos

El script automáticamente:
- ✅ Despliega infraestructura (VPC, RDS, Lambda, API Gateway, S3, CloudFront)
- ✅ Construye y sube imagen Docker a ECR
- ✅ Actualiza función Lambda
- ✅ Construye y despliega frontend a S3
- ✅ Invalida caché de CloudFront

### 3. Acceder a tu aplicación

Al finalizar, verás las URLs:

```
API: https://xxxxx.execute-api.us-east-1.amazonaws.com/dev
Frontend: https://xxxxx.cloudfront.net
```

## 📋 Requisitos Previos

- AWS CLI configurado (`aws configure`)
- Terraform >= 1.0 instalado
- Docker instalado
- Node.js y npm instalados

## 🎯 Comandos Útiles

### Ver estado actual

```bash
terraform show
```

### Ver outputs

```bash
terraform output
terraform output deployment_summary
```

### Actualizar solo backend

```bash
./deploy.sh --skip-infra --skip-frontend
```

### Actualizar solo frontend

```bash
./deploy.sh --skip-infra --skip-backend
```

### Destruir todo

```bash
chmod +x destroy.sh
./destroy.sh
```

## 🏗️ Infraestructura Desplegada

| Recurso | Descripción | Costo Aprox. |
|---------|-------------|--------------|
| VPC | Red privada con 2 AZs | Gratis |
| RDS PostgreSQL | db.t3.micro | $15/mes |
| Lambda | 512MB, contenedor | $5-10/mes |
| API Gateway | HTTP API | $3.50/mes |
| S3 | Hosting frontend | $0.23/mes |
| CloudFront | CDN global | $1/mes |
| ECR | Registry de imágenes | $0.10/mes |
| **Total** | | **~$25-30/mes** |

## 🔧 Configuración Avanzada

### Usar dominio personalizado

1. Crea certificado ACM en `us-east-1`
2. Agrega a `terraform.tfvars`:

```hcl
domain_name     = "app.tudominio.com"
certificate_arn = "arn:aws:acm:us-east-1:123456789012:certificate/..."
```

3. Actualiza DNS para apuntar a CloudFront

### Cambiar región

```hcl
aws_region = "eu-west-1"  # o cualquier región
```

### Ajustar recursos Lambda

```hcl
lambda_memory_size = 1024  # MB
lambda_timeout     = 60    # segundos
```

### Deshabilitar CloudFront (solo S3)

```hcl
enable_cloudfront = false
```

## 🔒 Seguridad

### Mejores prácticas implementadas:

- ✅ Base de datos en subnets privadas
- ✅ Encriptación en reposo (RDS, S3)
- ✅ Encriptación en tránsito (HTTPS/TLS)
- ✅ Secrets Manager para credenciales
- ✅ Security Groups restrictivos
- ✅ IAM roles con mínimos privilegios
- ✅ CloudWatch logging habilitado

### Para producción:

1. **State remoto**: Usa S3 + DynamoDB para Terraform state
2. **CORS**: Especifica dominios exactos en `allowed_origins`
3. **Backups**: RDS backups automáticos habilitados
4. **Monitoring**: Configura alarmas en CloudWatch
5. **WAF**: Habilita `enable_waf = true`

## 📊 Monitoreo

### CloudWatch Logs

```bash
# Ver logs de Lambda
aws logs tail /aws/lambda/carddemo-dev-api --follow

# Ver logs de API Gateway
aws logs tail /aws/apigateway/carddemo-dev --follow
```

### Métricas

Accede a CloudWatch Console para ver:
- Invocaciones de Lambda
- Latencia de API Gateway
- Conexiones a RDS
- Transferencia de CloudFront

## 🐛 Troubleshooting

### Error: "Image not found"

La primera vez, necesitas construir la imagen manualmente:

```bash
cd ../carddemo-api
ECR_URL=$(cd ../terraform && terraform output -raw ecr_repository_url)
aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin $ECR_URL
docker build -t $ECR_URL:latest -f Dockerfile.lambda .
docker push $ECR_URL:latest
```

Luego ejecuta `terraform apply` de nuevo.

### Error: "Bucket already exists"

Los nombres de buckets S3 son globales. El script usa un sufijo aleatorio, pero si falla:

```bash
terraform destroy
terraform apply
```

### Lambda no puede conectar a RDS

Verifica que:
1. Lambda está en las subnets privadas
2. Security groups permiten tráfico
3. RDS endpoint es correcto en variables de entorno

## 📚 Documentación Completa

- `terraform/README.md` - Documentación detallada de Terraform
- `AWS_MIGRATION_GUIDE.md` - Guía manual paso a paso
- `AWS_MIGRATION_SUMMARY.md` - Resumen de arquitectura

## 🎓 Aprender Más

- [Terraform AWS Provider](https://registry.terraform.io/providers/hashicorp/aws/latest/docs)
- [AWS Lambda Containers](https://docs.aws.amazon.com/lambda/latest/dg/images-create.html)
- [API Gateway HTTP APIs](https://docs.aws.amazon.com/apigateway/latest/developerguide/http-api.html)

## 💡 Tips

1. **Desarrollo local primero**: Prueba todo localmente antes de desplegar
2. **Usa variables**: No hardcodees valores en los archivos .tf
3. **State remoto**: Para equipos, usa S3 backend
4. **Módulos**: Para proyectos grandes, organiza en módulos
5. **Versionado**: Usa tags de Git para versionar infraestructura

## 🤝 Soporte

¿Problemas? Abre un issue en GitHub con:
- Logs de Terraform
- Logs de CloudWatch
- Configuración (sin credenciales)

---

**¡Listo para desplegar!** 🚀

```bash
cd terraform
./deploy.sh
```
