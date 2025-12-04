# Kiro Workspace

This project contains:
- **backend/**: FastAPI Python application
- **infrastructure/**: AWS CDK Infrastructure as Code

## Quick Start

### Backend
```bash
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
uvicorn main:app --reload
```

### Infrastructure
```bash
cd infrastructure
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cdk deploy
```
