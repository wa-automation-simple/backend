# WhatsApp Marketing SaaS - Microservices Backend

Complete Python microservices backend for WhatsApp Marketing SaaS platform with all required features.

## 🚀 Fitur Utama

### 1. **Panasin WA (WhatsApp Warming)**
- Progressive 30-day warming schedule
- Automated daily message limits
- Status tracking and monitoring

### 2. **Blast WA**
- Bulk messaging campaigns
- Scheduled sending
- Real-time status tracking

### 3. **Blast dengan Gambar**
- Media upload endpoint (images, videos, documents)
- Cloud storage integration ready
- Multi-format support

### 4. **Auto-Reply dengan AI**
- Keyword-based triggers
- AI-powered responses using tokens
- Context-aware conversations

### 5. **Token System dengan Markup**
- Base price: $3/token (provider cost)
- Sell price: $10/token (user price)
- 233% markup profit margin
- Top-up via payment gateway

### 6. **Follow-up Member**
- Schedule follow-ups
- Track completion status
- Overdue notifications

### 7. **Multi-Account Support**
- One app, multiple WhatsApp logins
- Account switching
- Per-account settings

### 8. **Auto-Click Recovery**
- Generate recovery links for banned accounts
- Automatic link clicking
- Status monitoring

## 📁 Struktur Project

```
microservices/
├── shared/                 # Shared library
│   ├── config/            # Configuration
│   ├── models/            # SQLAlchemy models + RBAC
│   ├── schemas/           # Pydantic serializers
│   └── utils/             # Auth, database helpers
├── gateway/               # API Gateway (port 8000)
├── auth-service/          # Authentication (port 8001)
├── whatsapp-service/      # WhatsApp management (port 8003)
├── blast-service/         # Blast campaigns (port 8004)
├── ai-service/            # AI & tokens (port 8005)
├── payment-service/       # Payments (port 8006)
├── followup-service/      # Follow-ups (port 8007)
└── scheduler-service/     # Background tasks (port 8008)
```

## 🔐 RBAC (Role-Based Access Control)

| Role | Permissions |
|------|-------------|
| `super_admin` | Full access to everything |
| `admin` | User management, billing, analytics |
| `manager` | Campaigns, blast, follow-ups |
| `user` | Basic messaging, token top-up |
| `trial` | Limited read-only access |

## 🛠️ Tech Stack

- **Framework**: FastAPI
- **Database**: PostgreSQL
- **Cache**: Redis
- **Validation**: Pydantic (Django-like serializers)
- **Auth**: JWT with RBAC
- **Container**: Docker & Docker Compose

## 🚀 Quick Start

### Using Docker Compose

```bash
cd microservices

# Start all services
docker-compose up -d

# Check service health
curl http://localhost:8000/services/health
```

### Manual Setup

```bash
# Install dependencies
pip install -r requirements.txt

# Set environment variables
export DATABASE_URL=postgresql://postgres:postgres@localhost:5432/wa_saas
export REDIS_URL=redis://localhost:6379/0

# Run individual services
python -m uvicorn gateway.main:app --port 8000
python -m uvicorn auth_service.main:app --port 8001
# ... etc
```

## 📡 API Endpoints

### Gateway (Port 8000)
- `GET /` - API info
- `GET /health` - Gateway health
- `GET /services/health` - All services health
- `/{service}/{path}` - Proxy to any service

### Auth Service (Port 8001)
- `POST /auth/register` - Register user
- `POST /auth/login` - Login & get token
- `GET /auth/me` - Current user info
- `PUT /auth/me` - Update profile

### WhatsApp Service (Port 8003)
- `POST /accounts` - Add WhatsApp account
- `GET /accounts` - List accounts
- `POST /warmup/start` - Start warming
- `POST /accounts/{id}/recovery-link` - Generate recovery

### Blast Service (Port 8004)
- `POST /campaigns` - Create campaign
- `POST /media/upload` - Upload image/video
- `POST /campaigns/{id}/send` - Send blast

### AI Service (Port 8005)
- `POST /auto-reply` - Create auto-reply
- `POST /ai/generate` - Generate AI response
- `GET /tokens/balance` - Check balance
- `POST /tokens/topup` - Top-up tokens ($10/token)

### Payment Service (Port 8006)
- `POST /payments` - Create payment
- `GET /pricing` - Token pricing info

### Follow-up Service (Port 8007)
- `POST /followups` - Create follow-up
- `POST /followups/{id}/execute` - Execute follow-up

### Scheduler Service (Port 8008)
- `POST /warmup/execute/{id}` - Run warmup task
- `POST /blast/execute-pending` - Run pending blasts
- `POST /recovery/auto-click/{id}` - Auto-click recovery

## 💰 Token Pricing

```json
{
  "base_price_per_token": 3.0,
  "sell_price_per_token": 10.0,
  "markup_percentage": 233.33,
  "packages": [
    {"tokens": 10, "price": 100, "savings": 0},
    {"tokens": 50, "price": 475, "savings": "5%"},
    {"tokens": 100, "price": 900, "savings": "10%"},
    {"tokens": 500, "price": 4250, "savings": "15%"}
  ]
}
```

## 📝 Environment Variables

Create `.env` file:

```env
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/wa_saas
REDIS_URL=redis://localhost:6379/0
JWT_SECRET_KEY=your-super-secret-key
AI_API_KEY=sk-your-openai-key
```

## 🧪 Testing

```bash
# Run tests
pytest

# Test specific service
curl -X POST http://localhost:8001/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"Test1234!"}'
```

## 📄 License

MIT License
