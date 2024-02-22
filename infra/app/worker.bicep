param name string
param location string = resourceGroup().location
param tags object = {}

param applicationInsightsName string
param containerAppsEnvironmentName string
param containerRegistryName string
param imageName string = ''
param serviceName string = 'chatbot'
param managedIdentityName string = ''
param dbserverDomainName string
param dbserverDatabaseName string
param dbserverUser string

@secure()
param dbserverPassword string

@secure()
param telegramAccessToken string


module app '../core/host/container-app-worker.bicep' = {
  name: '${serviceName}-container-app-module'
  params: {
    name: name
    location: location
    tags: union(tags, { 'azd-service-name': 'worker' })
    containerAppsEnvironmentName: containerAppsEnvironmentName
    containerRegistryName: containerRegistryName
    imageName: !empty(imageName) ? imageName : 'nginx:latest'
    daprEnabled: true
    containerName: serviceName
    managedIdentityEnabled: true
    managedIdentityName: managedIdentityName
    env: [
      {
        name: 'TELEGRAM_ACCESS_TOKEN'
        secretRef: 'telegram-accesstoken'
      }
      {
        name: 'POSTGRES_HOST'
        value: dbserverDomainName
      }
      {
        name: 'POSTGRES_USERNAME'
        value: dbserverUser
      }
      {
        name: 'POSTGRES_DATABASE'
        value: dbserverDatabaseName
      }
      {
        name: 'POSTGRES_PASSWORD'
        secretRef: 'dbserver-password'
      }
      {
        name: 'POSTGRES_SSL'
        value: 'require'
      }
      {
        name: 'RUNNING_IN_PRODUCTION'
        value: 'true'
      }
      {
        name: 'APPLICATIONINSIGHTS_CONNECTION_STRING'
        value: applicationInsights.properties.ConnectionString
      }
    ]
    secrets: [
      {
        name: 'dbserver-password'
        value: dbserverPassword
      }
      {
        name: 'telegram-accesstoken'
        value: telegramAccessToken
      }
    ]
  }
}

resource applicationInsights 'Microsoft.Insights/components@2020-02-02' existing = {
  name: applicationInsightsName
}

output SERVICE_WEB_IDENTITY_PRINCIPAL_ID string = app.outputs.identityPrincipalId
output SERVICE_WEB_NAME string = app.outputs.name
output SERVICE_WEB_IMAGE_NAME string = app.outputs.imageName
