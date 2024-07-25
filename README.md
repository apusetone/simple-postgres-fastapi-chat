# simple-postgres-fastapi-chat

This project demonstrates how to implement a real-time chat application using FastAPI, PostgreSQL's `NOTIFY/LISTEN` feature, SQLAlchemy, and WebSockets. Podman and Kind are used to orchestrate the services. PDM is used for Python package management.

## Features

- Real-time chat using WebSockets and PostgreSQL's NOTIFY/LISTEN mechanism
- Message persistence in PostgreSQL database
- Asynchronous database operations with SQLAlchemy and asyncpg
- FastAPI for efficient API development
- Use of PostgreSQL NOTIFY/LISTEN for real-time message broadcasting
- Podman and Kind for easy deployment and development
- PDM for Python package management

## Prerequisites

Make sure you have the following installed on your machine:

- [Podman](https://podman.io/getting-started/installation)
- [Kind](https://kind.sigs.k8s.io/docs/user/quick-start/#installation)
- [PDM](https://pdm.fming.dev/latest/)

## Setup Instructions

### 1. Install Podman and Kind

First, ensure that Podman and Kind are installed on your machine. Follow the installation guides:

- [Podman Installation Guide](https://podman.io/getting-started/installation)
- [Kind Installation Guide](https://kind.sigs.k8s.io/docs/user/quick-start/#installation)

### 2. Set Up Environment Variables

Create a copy of the example environment file and adjust the values:

```sh
cp .env.bak .env
```

Open the `.env` file in a text editor and adjust the values as needed for your environment. This file contains important configuration settings for your application.

### 3. Create a Kind Cluster with Podman

Set the experimental provider for Kind to use Podman:

```sh
export KIND_EXPERIMENTAL_PROVIDER=podman
```

Create a Kind cluster using the provided configuration file:

```sh
kind create cluster --config kind-config.yaml
```

### 4. Build the Application

Build the Podman image for your FastAPI application:

```sh
podman build -t localhost/fastapi:latest -f Containerfile .
```

Save the built image to a tar file:

```sh
mkdir target; podman save localhost/fastapi:latest -o target/fastapi.tar
```

Load the image into the Kind cluster:

```sh
kind load image-archive target/fastapi.tar --name podman-kind
```

### 5. Deploy the Application and Database

Create a ConfigMap from the environment file:

```sh
kubectl create configmap fastapi-config --from-env-file=.env
```

Apply the Kubernetes manifests to deploy the application and database:

```sh
kubectl apply -f k8s-manifests.yaml
```

Check the status of the pods:

```sh
kubectl get pods
```

### 6. Create PostgreSQL Database

To create the PostgreSQL database, execute the following commands:

```sh
kubectl exec -it $(kubectl get pods | grep postgresql | awk '{print $1}') -- /bin/bash
```

Once inside the PostgreSQL container, run:

```sh
psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" <<-EOSQL
    SELECT 'CREATE DATABASE mydatabase'
    WHERE NOT EXISTS (SELECT FROM pg_database WHERE datname = 'mydatabase');\\gexec
EOSQL
```

### 7. Run Database Migrations

After the services are up, apply the database migrations:

```sh
kubectl exec -it $(kubectl get pods | grep fastapi | awk '{print $1}') -- alembic upgrade head
```

### 8. Access the Application

The FastAPI application will be accessible at `http://localhost:8000`.

You can access the API documentation at `http://localhost:8000/docs`.

### 9. Stop the Application

To stop the Kind cluster:

```sh
kind delete cluster --name podman-kind
```

## Usage

### API Endpoints

- `POST /messages/`: Create a new message
- `WebSocket /ws`: WebSocket endpoint for real-time chat

### Interact with the API

You can interact with the API using a tool like `curl`, `httpie`, or Postman.

#### Create a new chat message

```sh
curl -X POST "http://localhost:8000/messages/" -H "Content-Type: application/json" -d '{"username": "user1", "message": "Hello, world!"}'
```

### WebSocket Connection

You can connect to the WebSocket endpoint to receive real-time updates of new chat messages. Use a WebSocket client like [websocat](https://github.com/vi/websocat), [Postman](https://www.postman.com/), or a custom frontend.

```sh
wscat -c ws://localhost:8000/ws
```

## Project Structure

The project structure is organized as follows:

```sh
.
├── Containerfile
├── LICENSE
├── README.md
├── alembic.ini
├── app
│   ├── __init__.py
│   ├── config
│   ├── database.py
│   ├── main.py
│   ├── models.py
│   └── utils.py
├── k8s-manifests.yaml
├── kind-config.yaml
├── migrations
│   ├── env.py
│   ├── script.py.mako
│   └── versions
│       └── 9152b24fc6d1_initial_migration.py
├── pdm.lock
├── pyproject.toml
└── tests
    ├── __init__.py
```

### Key Files and Directories

- `Containerfile`: The container file used to build the FastAPI application image.
- `LICENSE`: The license file for the project.
- `README.md`: The readme file you are currently reading.
- `alembic.ini`: Configuration file for Alembic, used for database migrations.
- `app/`: The main application directory.
  - `__init__.py`: Initialization file for the app module.
  - `config/`: Directory for configuration files.
  - `database.py`: Database connection and setup.
  - `main.py`: The main entry point for the FastAPI application.
  - `models.py`: Database models.
  - `utils.py`: Utility functions.
- `k8s-manifests.yaml`: Kubernetes manifests for deploying the application and database.
- `kind-config.yaml`: Configuration file for creating the Kind cluster.
- `migrations/`: Directory for database migration scripts.
  - `env.py`: Environment configuration for Alembic.
  - `script.py.mako`: Template for Alembic migration scripts.
  - `versions/`: Directory containing individual migration scripts.
    - `9152b24fc6d1_initial_migration.py`: Initial database migration script.
- `pdm.lock`: Lock file for PDM, ensuring consistent package versions.
- `pyproject.toml`: Configuration file for PDM and project dependencies.
- `tests/`: Directory for test cases.
  - `__init__.py`: Initialization file for the tests module.

## How it works

1. Users connect to the WebSocket endpoint
2. Messages are stored in the PostgreSQL database
3. PostgreSQL NOTIFY is used to broadcast new messages
4. Connected clients receive real-time updates

## Development

To set up the development environment:

1. Install PDM if you haven't already
2. Run `pdm install` to install dependencies
3. Use `pdm run` to run scripts defined in `pyproject.toml`
