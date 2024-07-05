# simple-postgres-fastapi-chat

This project demonstrates how to implement a real-time chat application using FastAPI, PostgreSQL's `NOTIFY/LISTEN` feature, SQLAlchemy, and WebSockets. Docker Compose is used to orchestrate the services. PDM is used for Python package management.

## Features

- Real-time chat using WebSockets and PostgreSQL's NOTIFY/LISTEN mechanism
- Message persistence in PostgreSQL database
- Asynchronous database operations with SQLAlchemy and asyncpg
- FastAPI for efficient API development
- Use of PostgreSQL NOTIFY/LISTEN for real-time message broadcasting
- Docker Compose for easy deployment and development
- PDM for Python package management

## Prerequisites

Make sure you have the following installed on your machine:

- [Docker](https://docs.docker.com/get-docker/)
- [Docker Compose](https://docs.docker.com/compose/install/)
- [PDM](https://pdm.fming.dev/latest/)

## Setup Instructions

### 1. Set Up Environment Variables

First, create a copy of the example environment file and adjust the values:

```sh
cp .env.bak .env
```

Open the `.env` file in a text editor and adjust the values as needed for your environment. This file contains important configuration settings for your application.

### 2. Build the Application

After setting up your environment variables, build the Docker images:

```sh
docker-compose build
```

This command will build the Docker images for your FastAPI application and any other services defined in your `docker-compose.yml`.

### 3. Run the Application and Database

Start the application and database services:

```sh
docker-compose up -d
```

This will start both the FastAPI application and the PostgreSQL database in detached mode.

### 4. Run Database Migrations

After the services are up, apply the database migrations:

```sh
docker-compose exec fastapi alembic upgrade head
```

This command runs the Alembic migrations to set up your database schema.

### 5. Access the Application

The FastAPI application will be accessible at `http://localhost:8000`.

You can access the API documentation at `http://localhost:8000/docs`.

### 6. Stop the Application

To stop the running containers:

```sh
docker-compose down
```

If you want to stop the containers and remove the volumes, use:

```sh
docker-compose down -v
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

```
.
├── Dockerfile
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
├── compose.yml
├── migrations
│   ├── env.py
│   ├── script.py.mako
│   └── versions
├── pdm.lock
├── pyproject.toml
└── tests
    └── __init__.py
```

- `Dockerfile`: Defines the Docker build and runtime environment for the application.
- `LICENSE`: Contains the project's license information.
- `README.md`: Provides project description and usage instructions (this file).
- `alembic.ini`: Configuration file for Alembic, used for database migrations.
- `app/`: Directory containing the main application code.
  - `__init__.py`: Defines the app directory as a Python package.
  - `config/`: Directory for application configuration files.
  - `database.py`: Handles database connection and session management.
  - `main.py`: Main entry point for the FastAPI application.
  - `models.py`: Defines SQLAlchemy models.
  - `utils.py`: Contains utility functions and helper classes.
- `compose.yml`: Docker Compose configuration file for defining and managing multiple Docker containers.
- `migrations/`: Directory for Alembic migration files.
  - `env.py`: Alembic environment configuration script.
  - `script.py.mako`: Template for migration scripts.
  - `versions/`: Directory to store individual migration scripts.
- `pdm.lock`: PDM dependency lock file.
- `pyproject.toml`: Defines project metadata and dependencies.
- `tests/`: Directory for test code.

This structure represents a typical project setup combining a FastAPI application, database migrations (Alembic), Docker containerization, and dependency management using PDM.

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
