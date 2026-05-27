# WhatsApp Marketing SaaS - Microservices Backend

A comprehensive microservices backend for WhatsApp Marketing SaaS platform with RBAC, multi-account support, and AI-powered features.

## 📁 Project Structure

```
microservices/
├── shared/                          # Shared library (used by all services)
│   ├── config/
│   │   └── settings.py              # Configuration & environment variables
│   ├── models/
│   │   ├── rbac.py                  # Role-Based Access Control (5 roles, 30+ permissions)
│   │   └── tables.py                # SQLAlchemy database models
│   ├── schemas/
│   │   └── serializers.py           # Pydantic validators (Django-like serializers)
│   ├── utils/
│   │   └── auth.py                  # JWT authentication utilities
│   └── __init__.py
│
├── gateway/                         # API Gateway (port 8000)
├── auth-service/                    # Authentication Service (port 8001)
│   ├── config/
│   │   └── database.py              # Database connection (own DB)
│   ├── models/
│   │   └── user.py                  # User model
│   ├── services/
│   │   ├── auth_service.py          # Password hashing
│   │   └── user_service.py          # User CRUD operations
│   ├── routes/
│   │   └── auth_routes.py           # Auth endpoints
│   └── main.py                      # FastAPI app
│
├── whatsapp-service/                # WhatsApp Management (port 8003)
│   ├── config/database.py           # Database connection (own DB)
│   ├── models/whatsapp.py           # WhatsApp account models
│   ├── services/whatsapp_service.py # Account & warming logic
│   ├── routes/whatsapp_routes.py    # WhatsApp endpoints
│   └── main.py
│
├── blast-service/                   # Blast Campaigns (port 8004)
├── ai-service/                      # AI & Auto-Reply (port 8005)
├── payment-service/                 # Payments & Tokens (port 8006)
├── followup-service/                # Follow-up Management (port 8007)
└── scheduler-service/               # Background Tasks (port 8008)
```

## 🔐 RBAC System

### Roles (5 levels)
- **super_admin**: Full access to everything
- **admin**: Manage users, accounts, campaigns
- **manager**: Manage accounts, campaigns, follow-ups
- **user**: Standard user features
- **trial**: Read-only access, limited features

### Permissions (30+)
- User management: `user:create`, `user:read`, `user:update`, `user:delete`
- WhatsApp: `wa_account:*`, `wa_warmup:*`
- Blast: `blast:*`, `blast:with_media`
- AI: `ai:use`, `auto_reply:*`
- Tokens: `token:buy`, `token:read`
- Follow-up: `followup:*`
- Recovery: `recovery:manage`, `auto_click:enable`

## 💰 Token Pricing (Markup Model)

| Item | Base Cost | Sell Price | Markup |
|------|-----------|------------|--------|
| 1 AI Token | $3.00 | $10.00 | 233% |

**Bulk Packages:**
- 10 tokens: $90 (10% discount)
- 50 tokens: $400 (20% discount)
- 100 tokens: $700 (30% discount)

## 🚀 Features Implemented

1. ✅ **Panasin WA** - 30-day progressive warming schedule
2. ✅ **Blast WA** - Bulk messaging with campaign management
3. ✅ **Blast dengan Gambar** - Media upload for images/videos
4. ✅ **Auto-Reply AI** - Contextual AI responses with token usage
5. ✅ **Token System** - Markup pricing from $3 to $10
6. ✅ **Follow-up Member** - Schedule and track follow-ups
7. ✅ **Multi-Account** - One app, multiple WhatsApp logins
8. ✅ **Auto-Click Recovery** - Automatic recovery link clicking

## 🛠️ Tech Stack

- **Framework**: FastAPI
- **Database**: PostgreSQL (separate DB per service)
- **ORM**: SQLAlchemy
- **Validation**: Pydantic (Django-like serializers)
- **Auth**: JWT with OAuth2
- **Container**: Docker & Docker Compose

## 📡 API Ports

| Service | Port | Database |
|---------|------|----------|
| Gateway | 8000 | - |
| Auth | 8001 | auth_service_db |
| WhatsApp | 8003 | whatsapp_service_db |
| Blast | 8004 | blast_service_db |
| AI | 8005 | ai_service_db |
| Payment | 8006 | payment_service_db |
| Follow-up | 8007 | followup_service_db |
| Scheduler | 8008 | scheduler_service_db |

## 🏃 Quick Start

### Prerequisites
- Docker & Docker Compose
- Python 3.11+ (for local development)

### Run with Docker

```bash
cd microservices

# Set environment variables (optional)
export OPENAI_API_KEY=your_key_here
export STRIPE_SECRET_KEY=your_key_here

# Start all services
docker-compose up -d

# View logs
docker-compose logs -f

# Stop all services
docker-compose down
```

### Local Development

```bash
# Install dependencies
pip install -r requirements.txt

# Set environment variables
export DATABASE_URL=postgresql://postgres:postgres@localhost:5432/auth_service_db

# Run individual service
cd auth-service
python main.py
```

## 📝 API Endpoints

### Auth Service (`/auth`)
- `POST /register` - Register new user
- `POST /login` - Login and get token
- `GET /me` - Get current user
- `PUT /me` - Update profile
- `POST /change-password` - Change password

### WhatsApp Service (`/whatsapp`)
- `POST /accounts` - Add WhatsApp account
- `GET /accounts` - List all accounts
- `POST /warmup/start` - Start warming
- `GET /warmup/status/{id}` - Get warming status
- `GET /recovery-link/{id}` - Get recovery link
- `POST /auto-click/toggle` - Toggle auto-click

## 📊 Database Architecture

Each microservice has its **own isolated database**:
- No shared database connections
- Services communicate via API calls
- Better scalability and fault isolation
- Independent migrations and backups

## 🔒 Security

- JWT token authentication
- Password hashing with bcrypt
- Role-based access control (RBAC)
- Permission-based endpoint protection
- CORS configuration

## 📄 License

MIT License
