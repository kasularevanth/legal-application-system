
# ============ deployment/azure/deploy.sh ============
#!/bin/bash

# Azure deployment script for Legal Application System

set -e

# Configuration
RESOURCE_GROUP="legal-app-rg"
LOCATION="East US"
APP_NAME="legal-application-system"
DB_NAME="legal-app-db"
STORAGE_ACCOUNT="legalappstorage"

echo "Starting Azure deployment..."

# Create resource group
echo "Creating resource group..."
az group create --name $RESOURCE_GROUP --location "$LOCATION"

# Create PostgreSQL server
echo "Creating PostgreSQL server..."
az postgres server create \
  --resource-group $RESOURCE_GROUP \
  --name $DB_NAME \
  --location "$LOCATION" \
  --admin-user legalapp \
  --admin-password "YourSecurePassword123!" \
  --sku-name B_Gen5_1 \
  --version 11

# Create database
az postgres db create \
  --resource-group $RESOURCE_GROUP \
  --server-name $DB_NAME \
  --name legalappdb

# Create storage account
echo "Creating storage account..."
az storage account create \
  --name $STORAGE_ACCOUNT \
  --resource-group $RESOURCE_GROUP \
  --location "$LOCATION" \
  --sku Standard_LRS

# Create App Service plan
echo "Creating App Service plan..."
az appservice plan create \
  --name "$APP_NAME-plan" \
  --resource-group $RESOURCE_GROUP \
  --location "$LOCATION" \
  --sku B1 \
  --is-linux

# Create web app for backend
echo "Creating backend web app..."
az webapp create \
  --resource-group $RESOURCE_GROUP \
  --plan "$APP_NAME-plan" \
  --name "$APP_NAME-backend" \
  --runtime "PYTHON|3.11"

# Create web app for frontend
echo "Creating frontend web app..."
az webapp create \
  --resource-group $RESOURCE_GROUP \
  --plan "$APP_NAME-plan" \
  --name "$APP_NAME-frontend" \
  --runtime "NODE|18-lts"

# Configure app settings for backend
echo "Configuring backend app settings..."
az webapp config appsettings set \
  --resource-group $RESOURCE_GROUP \
  --name "$APP_NAME-backend" \
  --settings \
    DJANGO_SETTINGS_MODULE=legal_app_backend.settings \
    SECRET_KEY="your-secret-key-here" \
    DEBUG=False \
    DB_HOST="$DB_NAME.postgres.database.azure.com" \
    DB_NAME=legalappdb \
    DB_USER="legalapp@$DB_NAME" \
    DB_PASSWORD="YourSecurePassword123!" \
    AZURE_STORAGE_ACCOUNT_NAME=$STORAGE_ACCOUNT \
    BHASHINI_API_KEY="your-bhashini-api-key" \
    AZURE_OPENAI_ENDPOINT="your-azure-openai-endpoint" \
    AZURE_OPENAI_API_KEY="your-azure-openai-api-key"

# Deploy backend code
echo "Deploying backend..."
cd ../backend
zip -r ../deployment.zip .
az webapp deployment source config-zip \
  --resource-group $RESOURCE_GROUP \
  --name "$APP_NAME-backend" \
  --src ../deployment.zip

# Deploy frontend
echo "Building and deploying frontend..."
cd ../frontend
npm install
npm run build

az webapp deployment source config-zip \
  --resource-group $RESOURCE_GROUP \
  --name "$APP_NAME-frontend" \
  --src build.zip

echo "Deployment completed successfully!"
echo "Backend URL: https://$APP_NAME-backend.azurewebsites.net"
echo "Frontend URL: https://$APP_NAME-frontend.azurewebsites.net"