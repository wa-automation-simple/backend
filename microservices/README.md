# WhatsApp Marketing SaaS - Microservices Backend

## 📋 Project Overview

Complete Python microservices backend for WhatsApp Marketing SaaS platform with:
- **Panasin WA** - Automated 30-day warming schedule
- **Blast WA** - Bulk messaging campaigns
- **Blast dengan Gambar** - Media upload support
- **Auto-reply AI** - Token-based AI responses
- **Token System** - $3 base cost → $10 user price (233% markup)
- **Follow-up Member** - Lead tracking and scheduling
- **Multi-Account** - Multiple WhatsApp accounts per user
- **Auto-Click Recovery** - Automatic recovery link clicking

## 🏗️ Architecture

```
microservices/
├── shared/                    # Shared utilities (middleware & security only)
│   ├── middleware/
│   │   └── auth.py           # Auth & RBAC middleware
│   └── security/
│       └── rbac.py           # RBAC permissions & JWT utils
│
├── gateway/                   # API Gateway (port 8000)
├── auth-service/              # Authentication (port 8001) + auth-db
├── whatsapp-service/          # WhatsApp mgmt (port 8003) + whatsapp-db
├── blast-service/             # Blast campaigns (port 8004) + blast-db
├── ai-service/                # AI & tokens (port 8005) + ai-db
├── payment-service/           # Payments (port 8006) + payment-db
├── followup-service/          # Follow-ups (port 8007) + followup-db
└── scheduler-service/         # Background tasks (port 8008) + scheduler-db
```

## 🔐 RBAC System

**5 Roles:** `super_admin`, `admin`, `manager`, `user`, `trial`

**30+ Permissions:**
- User management: `user:create`, `user:read`, `user:update`, `user:delete`
- WhatsApp: `wa_account:*`, `wa_warmup:manage`, `wa_send:message`
- Blast: `blast:*`, `blast:with_media`
- AI: `ai:use`, `ai_token:*`, `auto_reply:manage`
- Follow-up: `followup:*`
- Payment: `payment:*`, `token:purchase`
- Recovery: `recovery:manage`, `auto_click:enable`

## 🚀 Quick Start

### Prerequisites
- Docker & Docker Compose
- Python 3.11+ (for local development)

### Run with Docker Compose

```bash
cd microservices

# Set environment variables
export JWT_SECRET_KEY="your-super-secret-key"
export OPENAI_API_KEY="sk-your-openai-key"
export STRIPE_SECRET_KEY="sk-stripe-key"

# Start all services
docker-compose up -d

# Check status
docker-compose ps

# View logs
docker-compose logs -f auth-service
```

### Services & Ports

| Service | Port | Database |
|---------|------|----------|
| Gateway | 8000 | - |
| Auth | 8001 | auth-db:5432 |
| WhatsApp | 8003 | whatsapp-db:5432 |
| Blast | 8004 | blast-db:5432 |
| AI | 8005 | ai-db:5432 |
| Payment | 8006 | payment-db:5432 |
| Followup | 8007 | followup-db:5432 |
| Scheduler | 8008 | scheduler-db:5432 |
| Redis | 6379 | - |

## 📝 API Endpoints

### Auth Service (`/api/v1/auth`)
- `POST /register` - Register new user
- `POST /login` - Login & get tokens
- `GET /me` - Get current user profile
- `PUT /me` - Update profile
- `POST /change-password` - Change password
- `GET /permissions` - Get user permissions

### WhatsApp Service (`/api/v1`)
- `POST /accounts` - Create WhatsApp account
- `GET /accounts` - List accounts
- `POST /accounts/{id}/qr` - Generate QR code
- `POST /accounts/{id}/warmup/start` - Start warming
- `GET /accounts/{id}/warmup/status` - Get warmup status
- `POST /accounts/{id}/recovery/link` - Get recovery link
- `POST /accounts/{id}/recovery/auto-click/enable` - Enable auto-click

## 💰 Token Pricing

- **Base Cost**: $3/token (provider price)
- **Sell Price**: $10/token (user price)
- **Markup**: 233% profit
- **Bulk Discounts**: 5-15% for large packages

## 🗄️ Database Isolation

Each service has its own PostgreSQL database:
- Complete fault isolation
- Independent scaling
- Service-specific migrations
- No cross-service DB dependencies

## 🛠️ Development

### Local Setup (without Docker)

```bash
# Install dependencies
pip install -r requirements.txt

# Set environment variables
export DATABASE_URL="postgresql://postgres:postgres@localhost:5432/auth_db"

# Run service
cd auth-service
uvicorn main:app --reload --port 8001
```

### Running Tests

```bash
pytest tests/ -v
```

## 📦 Project Structure Example

Each service follows this structure:
```
service-name/
├── main.py                 # Entry point
├── config.py               # Pydantic settings
├── api/v1/
│   └── routes.py          # FastAPI routers
├── core/
│   └── database.py        # DB connection
├── models/
│   ├── model1.py          # Individual model files
│   └── model2.py
├── schemas/
│   └── serializers.py     # Pydantic validators
├── services/
│   └── business_logic.py  # Business logic
├── repositories/
│   └── data_access.py     # DB queries
└── migrations/            # Alembic migrations
```

## 🔧 Environment Variables

Create `.env` file in root:

```env
# Security
JWT_SECRET_KEY=your-super-secret-key

# AI
OPENAI_API_KEY=sk-your-openai-key

# Payments
STRIPE_SECRET_KEY=sk-stripe-key

# Database URLs (auto-configured in Docker)
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/db_name
```

## 📄 License

MIT License

## 👥 Support

For issues and questions, please open an issue on GitHub.
