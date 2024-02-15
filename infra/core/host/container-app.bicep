param name string
param location string = resourceGroup().location
param tags object = {}

param containerAppsEnvironmentName string = ''
param containerName string = 'main'
param containerRegistryName string = ''
param env array = []
param external bool = true
param imageName string
param keyVaultName string = ''
param managedIdentityEnabled bool = !empty(keyVaultName)
param managedIdentityName string = ''
param targetPort int = 80

param daprEnabled bool = false
param daprApp string = containerName
param daprAppProtocol string = 'http'

@description('CPU cores allocated to a single container instance, e.g. 0.5')
param containerCpuCoreCount string = '0.5'

@description('Memory allocated to a single container instance, e.g. 1Gi')
param containerMemory string = '1.0Gi'

resource app 'Microsoft.App/containerApps@2022-03-01' = {
  name: name
  location: location
  tags: tags
  identity: managedIdentityEnabled ? {
    type: 'SystemAssigned,UserAssigned'
    userAssignedIdentities: {
      '${managedIdentity.id}' : {}
    }
  } : { type: 'None' }
  dependsOn: [managedIdentity]
  properties: {
    managedEnvironmentId: containerAppsEnvironment.id
    configuration: {
      activeRevisionsMode: 'single'
      ingress: {
        external: external
        targetPort: targetPort
        transport: 'auto'
      }
      secrets: [
        {
          name: 'registry-password'
          value: containerRegistry.listCredentials().passwords[0].value
        }
        {
          name: 'telegram-access-token'
          value: '6942067828:AAEy5z02N1NEmYP2tVQLVnSRSDMlm-zWnOw'
        }
        {
          name: 'redis-password'
          value: '84DgAVAk5WXYvKoUEe1BAOHsCX6PXwrg'
        }
        {
          name: 'chatgpt-access-token'
          value: '05f203b4-44b1-4a94-bd9f-d6e9048012cf'
        }
      ]
      dapr: {
        enabled: daprEnabled
        appId: daprApp
        appProtocol: daprAppProtocol
        appPort: targetPort
      }
      registries: [
        {
          server: '${containerRegistry.name}.azurecr.io'
          username: containerRegistry.name
          passwordSecretRef: 'registry-password'
        }
      ]
    }
    template: {
      containers: [
        {
          image: imageName
          name: containerName
          env: [
            {
              name: 'TELEGRAM_ACCESS_TOKEN'
              secretRef: 'telegram-access-token'
            }
            {
              name: 'REDIS_PASSWORD'
              secretRef: 'redis-password'
            }
            {
              name: 'CHATGPT_ACCESS_TOKEN'
              secretRef: 'chatgpt-access-token'
            }
            {
              name: 'REDIS_HOST'
              value: 'redis-11851.c56.east-us.azure.cloud.redislabs.com'
            }
            {
              name: 'REDIS_PORT'
              value: '11851'
            }
            {
              name: 'CHATGPT_BASICURL'
              value: 'https://chatgpt.hkbu.edu.hk/general/rest'
            }
            {
              name: 'CHATGPT_MODELNAME'
              value: 'gpt-35-turbo-16k'
            }
            {
              name: 'CHATGPT_APIVERSION'
              value: '2023-12-01-preview'
            }
          ]
          resources: {
            cpu: json(containerCpuCoreCount)
            memory: containerMemory
          }
        }
      ]
      scale: {
        maxReplicas: 1
        minReplicas: 1
      }
    }
  }
}

resource containerAppsEnvironment 'Microsoft.App/managedEnvironments@2022-03-01' existing = {
  name: containerAppsEnvironmentName
}

// 2022-02-01-preview needed for anonymousPullEnabled
resource containerRegistry 'Microsoft.ContainerRegistry/registries@2022-02-01-preview' existing = {
  name: containerRegistryName
}

// user assigned managed identity to use throughout
resource managedIdentity 'Microsoft.ManagedIdentity/userAssignedIdentities@2022-01-31-preview' existing = {
  name: managedIdentityName
}

output identityPrincipalId string = managedIdentityEnabled ? app.identity.principalId : ''
output userManagedIdentitylId string = managedIdentityEnabled ? managedIdentity.id : ''
output imageName string = imageName
output name string = app.name
output uri string = 'https://${app.properties.configuration.ingress.fqdn}'
