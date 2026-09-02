![Python](https://img.shields.io/badge/Python-3.x-blue?logo=python)
![Django](https://img.shields.io/badge/Django-5.x-092E20?logo=django)
![Flask](https://img.shields.io/badge/Flask-3.x-black?logo=flask)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-16.x-336791?logo=postgresql)
![Docker](https://img.shields.io/badge/Docker-Containerised-2496ED?logo=docker)
![NGINX](https://img.shields.io/badge/NGINX-Reverse_Proxy-009639?logo=nginx&logoColor=white)
![AWS](https://img.shields.io/badge/AWS-EC2%20Deployment-FF9900?logo=amazonaws)
![OpenAPI](https://img.shields.io/badge/OpenAPI-Swagger-85EA2D?logo=swagger)
![Testing](https://img.shields.io/badge/Testing-pytest%20%7C%20Django_Test_Framework-0A9EDC)
![flake8](https://img.shields.io/badge/flake8-Code_Quality-306998)
![CI/CD](https://img.shields.io/badge/CI/CD-GitHub_Actions-2088FF?logo=githubactions&logoColor=white)
![CD](https://img.shields.io/badge/CD-Automated_Deployment-success?logo=githubactions&logoColor=white)
# Productivity Microservices Platform


A multi-service backend platform designed to demonstrate modern backend engineering using Django, Flask, Docker, and service-oriented architecture.

The platform enables users to manage projects, track work sessions, and interact with multiple backend services through a unified Django web interface.


This project focuses on scalable backend architecture, API-driven service communication, containerised development workflows, and production-style deployment practices.

**Live Demo:** https://productivity-app.xmattc.com/

You can create an account or use the demo login:

> Email: demo@example.com<br>
> Password: demo12345<br>
---

## 💡 Highlights

- Django Backend-for-Frontend (BFF)
- Three independent Flask microservices
- REST API design and inter-service communication
- PostgreSQL database per service
- Docker Compose development environment
- AWS EC2 deployment
- GitHub Actions CI/CD
- OpenAPI documentation
- Comprehensive automated test suite

---

## 🖼️ Application Screenshot

<p align="center">
    <img src="docs\images\dashboard_screenshot.png" width="800">
</p>

---

## 🛠️ Tech Stack

- **Backend:** Python, Django, Flask
- **Databases:** PostgreSQL
- **Architecture:** Microservices, REST APIs, Backend-for-Frontend, Service-Oriented Design
- **Infrastructure:** Docker, Docker Compose, AWS EC2
- **API Documentation:** OpenAPI / Swagger via flask-smorest
- **Testing & Quality:** Pytest, Django Test Framework, flake8

---

## 📈 System Architecture

A core focus of this project was designing clear service boundaries while maintaining a simple local development workflow. The platform is structured as independent backend services:

<p align="center">
  <img src="services\web\static\images\architecture.png" width="1000">
</p>

This architecture provides:

- Separation of business domains
- Independent database ownership and migrations
- Isolated API logic and responsibilities
- Improved maintainability and scalability
- Containerised local development using Docker Compose

The Django application acts as the primary Backend-for-Frontend (BFF) layer, while Flask services handle domain-specific functionality such as project management and time tracking.

[See the full architecture document](docs/architecture.md)

---

## 🔑 Key Features

- User registration and authentication
- Project management
- Kanban task management
- Time tracking with live session timer
- Dashboard with project insights
- OpenAPI documentation for every service
- Admin interface for user management
- Responsive web interface

---

## 🧱 Engineering Practices

- Automated testing covering API and model behaviour
- Dockerised development environment
- Environment-based configuration management
- Code quality enforcement using flake8
- Modular service-oriented application structure
- Test-Driven Development (TDD) applied to core features

### Development Workflow

- Test-Driven Development (TDD) workflows using feature branches
    - [Example incremental TDD commit history](https://github.com/xMattC/productivity-microservices-platform/commits/time-tracking-bff-client-TDD/)
- Pull request workflow for review and integration
    - [Closed PRs](https://github.com/xMattC/productivity-microservices-platform/pulls?q=is%3Apr+is%3Aclosed)
- Documented testing strategy and system guarantees
    - [Testing document](docs/testing.md)
- GitHub Actions CI/CD pipelines
    - Automated testing and linting on pull requests
    - Automated AWS EC2 deployment on merge to `main`
    - [Action History](https://github.com/xMattC/productivity-microservices-platform/actions)
    - [Example workflows](.github/workflows)
- Kanban-based project management
    - [Project board: Planning](https://github.com/users/xMattC/projects/4/views/1)
    - [Project board: Tasks](https://github.com/users/xMattC/projects/4/views/7)

---



## 📚 Service API Documentation

Each backend service includes dedicated API documentation.

| Service               | Documentation                                           |
| --------------------- | ------------------------------------------------------- |
| Projects Service      | [API Documentation](services/projects/docs/API.md)      |
| Time Tracking Service | [API Documentation](services/time-tracking/docs/API.md) |
| Tasks Service | [API Documentation](services/tasks/docs/API.md) |

The APIs are also documented using live OpenAPI / Swagger interfaces via `flask-smorest`.

### Example: Projects Service Swagger

![Projects Service Swagger](docs/images/projects_service_api_docs.PNG)



---

## 🔐 Authentication & Permissions

Authentication is handled by the Django web service using Django’s built-in authentication and session-based login flow.

Downstream Flask services receive the authenticated user context from the Django BFF via the `X-User-ID` request header.

Permissions and ownership are enforced through:

- Protected Django views for authenticated users
- User-scoped service requests from the Django BFF
- `X-User-ID` ownership checks in Flask services
- Database queries filtered by the authenticated user ID
- Service-level boundaries between web, projects, and time-tracking data

This ensures users only access project and time-tracking data associated with their own account while keeping service responsibilities separated.

---

## ⚠️ Validation & Error Handling

This includes:

- Request validation using Marshmallow schemas in Flask services
- Consistent service response structures using `results`
- Ownership checks using the authenticated user context
- User-scoped access validation through `X-User-ID`
- Service-client error handling in the Django BFF

Common responses include:

- `400 Bad Request` → Missing required request data or user context
- `404 Not Found` → Requested resource does not exist or does not belong to the user
- `5xx Service Error` → Downstream service unavailable or unexpected response

---

## ⚙️ Known Limitations

- Service-to-service communication is simplified for development and portfolio demonstration purposes
- Authentication and authorisation flows are intentionally lightweight
- Infrastructure focuses on Docker-based deployment rather than full production orchestration
- Advanced observability tooling (distributed tracing, metrics aggregation, alerting) is not implemented
- No horizontal scaling or container orchestration layer (e.g. Kubernetes)
- CI/CD pipelines currently target a single EC2 deployment environment
- APIs are internally structured but not versioned for public consumption
- Demo deployment may be reset or updated without notice

---

## 📦 Running Locally

### Prerequisites

Before running this project, ensure you have:

- Git (to clone the repository)
- Docker & Docker Compose (to run the application)

> If you're using Windows or macOS, install Docker Desktop which includes Docker Compose.

> Ensure Docker is running before completing steps 2 and 3. 

---

## 1. Clone Repository

```bash
git clone https://github.com/xMattC/productivity-microservices-platform.git
cd productivity-microservices-platform
```

---

## 2. Run Initial Setup


```bash
# Run database migrations for all services:
docker compose exec web python manage.py migrate
docker compose exec projects flask --app app.main:create_app db upgrade
docker compose exec time-tracking flask --app app.main:create_app db upgrade
docker compose exec tasks flask --app app.main:create_app db upgrade

# Seed demo user data:
docker compose exec web python manage.py seed_demo_data --reset
```
---

## 3. Start the Application

```bash
docker compose up
```


Web app: http://localhost:8000

You can create an account or use the demo login:
> Email: demo@example.com<br>
> Password: demo12345<br>

---
