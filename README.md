# 📋 KTypeform - Smart Form Automation

> AI-powered form builder with multi-step forms, conditional logic, PDF generation, and payment collection.

![Status](https://img.shields.io/badge/status-Production%20Ready-brightgreen)
![License](https://img.shields.io/badge/license-Proprietary-blue)

---

## ✨ Features

### Core Form Builder
- **AI-Powered Generation**: Describe your form in plain English, get a complete multi-step form
- **Multi-Step Forms**: Break long forms into pages with progress indicators
- **Jump Logic**: Skip pages based on user answers
- **Show/Hide Rules**: Conditionally display fields
- **Formulas**: Auto-calculate values based on other fields

### Output & Delivery
- **PDF Contracts**: Auto-generate branded PDF documents on submission
- **Email Notifications**: Send PDFs to respondents automatically
- **Cloud Storage**: PDFs stored in MinIO (S3-compatible)

### Team & Security
- **User Signup**: Self-service registration with isolated workspaces
- **Organization Invites**: Invite teammates via secure token links
- **API Keys**: Programmatic access for integrations

### Payments
- **Stripe Integration**: Collect payments before form submission (requires `STRIPE_SECRET_KEY`)

### Analytics
- **Dashboard**: View submission counts and trends
- **Charts**: Daily submission visualization

---

## 🚀 Quick Start

### Prerequisites
- Docker & Docker Compose
- Node.js 18+ (for local frontend development)

### 1. Clone & Configure
```bash
git clone <your-repo-url>
cd Ktypeform

# Copy example env (edit with your keys)
cp .env.example .env
```

### 2. Start the Stack
```bash
docker compose up -d
```

### 3. Access
- **Dashboard**: [http://localhost:3000](http://localhost:3000)
- **API Docs**: [http://localhost:8000/docs](http://localhost:8000/docs)
- **MinIO Console**: [http://localhost:9001](http://localhost:9001)

### Default Admin
- **Email**: `admin@example.com`
- **Password**: `password`

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        Frontend (Next.js)                       │
│                         localhost:3000                          │
└─────────────────────────────┬───────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                      Backend (FastAPI)                          │
│                         localhost:8000                          │
│  ┌────────────┐ ┌────────────┐ ┌────────────┐ ┌──────────────┐  │
│  │   Forms    │ │ Submissions│ │  AI Agent  │ │  Payments    │  │
│  │   API      │ │    API     │ │ (LangGraph)│ │  (Stripe)    │  │
│  └────────────┘ └────────────┘ └────────────┘ └──────────────┘  │
└───────┬─────────────┬─────────────┬─────────────┬───────────────┘
        │             │             │             │
        ▼             ▼             ▼             ▼
┌───────────┐  ┌───────────┐  ┌───────────┐  ┌───────────┐
│ PostgreSQL│  │   MinIO   │  │   Groq/   │  │  Stripe   │
│   (DB)    │  │  (S3/PDF) │  │  OpenAI   │  │   API     │
└───────────┘  └───────────┘  └───────────┘  └───────────┘
```

---

## 🔧 Environment Variables

| Variable | Description | Required |
|----------|-------------|----------|
| `SECRET_KEY` | JWT signing key | Yes |
| `POSTGRES_*` | Database config | Yes |
| `GROQ_API_KEY` | Groq LLM for AI generation | Yes (for AI) |
| `OPENROUTER_API_KEY` | OpenRouter fallback | Optional |
| `STRIPE_SECRET_KEY` | Stripe payments | Optional |
| `SMTP_HOST`, `SMTP_USER`, etc. | Email config | Optional |

---

## 📡 API Endpoints

### Authentication
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/v1/login/access-token` | OAuth2 login |
| POST | `/api/v1/signup` | Register new user |
| POST | `/api/v1/invite` | Invite teammate |
| POST | `/api/v1/join` | Accept invite |

### Forms
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/v1/forms/` | List forms |
| POST | `/api/v1/forms/` | Create form |
| GET | `/api/v1/forms/{id}` | Get form |
| POST | `/api/v1/forms/{id}/versions` | Create version |
| POST | `/api/v1/forms/{id}/versions/{v}/publish` | Publish version |

### Submissions
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/v1/forms/{slug}/submit` | Public form submission |
| GET | `/api/v1/forms/{id}/submissions` | List submissions |
| GET | `/api/v1/forms/{id}/stats` | Analytics stats |

### AI
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/v1/agents/generate` | Generate form from prompt |

### API Keys
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/v1/api-keys` | List keys |
| POST | `/api/v1/api-keys` | Create key |
| DELETE | `/api/v1/api-keys/{id}` | Revoke key |

### Payments
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/v1/payments/create-intent` | Create Stripe PaymentIntent |

---

## 🧪 Testing

```bash
# Run all E2E tests
python test_e2e.py
python test_signup.py
python test_invites.py
python test_api_keys.py
```

---

## 📦 Tech Stack

| Layer | Technology |
|-------|------------|
| Frontend | Next.js 14, React, Tailwind CSS, shadcn/ui |
| Backend | FastAPI, SQLAlchemy, Pydantic |
| Database | PostgreSQL |
| Storage | MinIO (S3-compatible) |
| AI | LangChain, LangGraph, Groq/OpenAI |
| Payments | Stripe |
| PDF | WeasyPrint |

---

## 📄 License

Proprietary - All rights reserved.

---

Built with ❤️ by the KTypeform Team
