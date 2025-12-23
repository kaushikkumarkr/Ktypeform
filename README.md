# KTypeform - Smart Form Automation SaaS

An AI-powered form builder that generates logic-driven forms, validations, and dynamic PDF contracts from natural language prompts.

![Tech Stack](https://img.shields.io/badge/Stack-Next.js_|_FastAPI_|_PostgreSQL-blue)
![Status](https://img.shields.io/badge/Status-MVP_Verified-green)

## 🚀 Features

### 🤖 AI Agent Layer
- **Generative Builder**: Describe your form (e.g., "Rental agreement with age check") and let the AI generate the Schema, Logic Rules, and PDF Template.
- **Multi-Provider**: Robust routing with fallbacks (Groq -> OpenRouter -> Hugging Face).

### 📝 Smart Form Engine
- **Logic Rules**: Conditional visibility (Show/Hide fields).
- **Formulas**: Computed fields (e.g., `quantity * price`).
- **Validation**: Schema-compliant constraints.

### 📄 Document Generation
- **PDF Contracts**: Automatically render filled PDFs using Jinja2 templates.
- **Storage**: Securely stored in MinIO (S3 compatible).

### 🔌 Integrations
- **Webhooks**: Trigger external workflows (e.g., **n8n**, Zapier) on submission.

## 🛠️ Tech Stack

- **Frontend**: Next.js 14, Shadcn UI, Tailwind CSS, TypeScript.
- **Backend**: FastAPI, SQLAlchemy, Pydantic, LangChain.
- **Database**: PostgreSQL 15.
- **Storage**: MinIO.
- **Orchestration**: Docker Compose.

## 🏁 Getting Started

### Prerequisites
- Docker & Docker Compose
- API Keys (Groq, OpenRouter, etc.) in `.env`

### Installation

1.  **Clone the repository**
2.  **Configure Environment**
    ```bash
    cp .env.example .env
    # Edit .env with your API keys
    ```
3.  **Start Services**
    ```bash
    docker compose up -d --build
    ```

### Usage

1.  **Access Dashboard**: [http://localhost:3000](http://localhost:3000)
    - **Login**: `admin@example.com` / `password`
2.  **Create Form**:
    - Click **Create Form**.
    - Go to **Editor**.
    - Click **Generate with AI** (Sparkles Icon).
    - Enter prompt: *"Job Application with score calculation"*.
3.  **Publish**: Click "Save & Publish".
4.  **Share**: Use the public link `/f/your-form-slug`.

## 🧪 Development

### Running E2E Tests
```bash
# Inside the root directory
# Ensure backend venv is active and dependencies installed
backend/venv/bin/python test_e2e.py
```

### Repo Structure
```
├── backend/          # FastAPI Application
│   ├── app/core/     # Logic (Agents, Validation, PDF)
│   └── ...
├── frontend/         # Next.js Application
├── docker-compose.yml
└── README.md
```

## 📜 License
MIT
