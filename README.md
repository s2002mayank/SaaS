# SaaS Wrapper  

A robust and scalable SaaS management application built using Django, Tailwind CSS, and Stripe. The project provides a seamless subscription-based payment system, social authentication, and a scalable backend for managing data effectively.

## 🚀 Features  
- **Subscription Management**: Supports flexible plans and automated billing using Stripe.  
- **Social Authentication**: Integrated authentication via Django-all-auth for Google and GitHub.  
- **Interactive UI**: A responsive frontend built with Tailwind CSS for an intuitive user experience.  
- **Scalable Architecture**: Utilizes a decentralized Postgres database for reliable data management.  
- **CI/CD**: Automated testing, deployment, and updates via GitHub Actions.  
- **Dockerized Deployment**: Consistent development, testing, and production environments with Docker.  

## 🛠️ Tech Stack  
| Technology          | Purpose                                   |  
|---------------------|-------------------------------------------|  
| Django              | Backend framework for robust logic and APIs.  |  
| Tailwind CSS        | Utility-first CSS framework for responsive UI. |  
| Stripe              | Payment gateway for subscription management. |  
| Docker              | Containerization for consistent deployment.  |  
| Postgres            | Database for scalable and reliable data management. |  
| GitHub Actions      | CI/CD pipeline for automated workflows.  |  
| Django-all-auth     | Social authentication integration.        |  

## Setup and Installation

### Prerequisites
- Python 3.9+
- Docker
- Stripe Account

### Local Development
1. Clone the repository
```bash
git clone https://github.com/yourusername/saas-wrapper.git
cd saas-wrapper
```

2. Create virtual environment
```bash
python -m venv venv
source venv/bin/activate
```

3. Install dependencies
```bash
pip install -r requirements.txt
```

4. Configure environment variables
- Create `.env` file
- Add Stripe, Django, and database configurations

### Docker Deployment
```bash
docker-compose up --build
```
