# Telegram Chatbot with OpenAI Integration

This Python-based Telegram chatbot application leverages the OpenAI API to intelligently respond to user queries. It is designed with a microservices architecture, deployed as container apps on Azure, and incorporates several advanced features including document upload and retrieval, chat history logging, and automated CI/CD workflows. This README provides detailed instructions for setting up, deploying, and managing the chatbot application.

## Key Features

- **OpenAI API Integration**: Enhances user interaction by generating intelligent responses to queries using OpenAI.
- **Document Management**: Allows for the upload of course PDF documents, storing them efficiently in a Pinecone vector database for quick reference during user queries, facilitated by the Langchain library.
- **Chat History Logging**: Utilizes a PostgreSQL database to log chat interactions with users.
- **Microservices Architecture**: Developed as microservices for scalability and maintainability, deployed as Azure Container Apps.
- **DAPR for Microservices**: Employs the DAPR framework for seamless communication between microservices.
- **Infrastructure as Code with Azure Bicep**: Streamlines infrastructure setup and management on Azure using Bicep templates.
- **Continuous Integration and Deployment**: Integrates GitHub Actions for CI/CD, automating the build and deployment process.
- **Docker Hub for Image Registry**: Utilizes Docker Hub to store and manage container images.

## Architecture Overview

The application's architecture is modular, consisting of separate microservices for handling different aspects of the chatbot's functionality, including interaction with the Telegram API, OpenAI processing, document management, and database operations. These components are orchestrated using DAPR to facilitate communication and data exchange.

## Getting Started

### Prerequisites

To deploy and run this application, you will need:

- An Azure account with the Azure CLI installed
- Docker and Docker Compose for local testing and container management
- A GitHub account for repository management and to set up CI/CD
- API tokens and credentials for Telegram, OpenAI, Pinecone, and PostgreSQL

### Initial Setup

1. **Clone the Repository**: Start by cloning this repository to your local machine.

2. **Deploy Infrastructure on Azure**: Use Azure Bicep to deploy the necessary infrastructure components. Navigate to the `infra` directory and run:
az login
az bicep install
az deployment group create --resource-group <your_resource_group_name> --template-file main.bicep

3. **Deploy the Application**: Use the Azure Developer CLI (azd) to deploy the application components to Azure.
azd up

4. **Configure Environment Variables**: Input below API tokens and database credentials on Azure application deployment:
TELEGRAM_API_TOKEN=<your_telegram_api_token>
OPENAI_API_TOKEN=<your_openai_api_token>
PINECONE_API_TOKEN=<your_pinecone_api_token>
POSTGRESQL_ADMIN_PASSWORD=<your_postgresql_admin_password>


## Deployment with GitHub Actions

The project is configured with GitHub Actions for CI/CD, automating the process of building Docker images, pushing them to Docker Hub, and deploying the updated images to Azure Container Apps upon every commit to the main branch.

## Project Structure

- `infra/`: Contains Azure Bicep files for the Azure infrastructure setup.
- `chatbot/` and `openai/`: Microservices Python applications for the chatbot and OpenAI integration.
- `.github/`: CI/CD configuration files for GitHub Actions.
- `Azd up`: Command support for deploying the application with Azure Developer CLI.

## Contributing

Contributions to this project are welcome! Please fork the repository, create a feature branch, and submit a pull request for review.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

